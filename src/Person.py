import Pyro4
import random
import configparser
from threading import Thread, Lock
import socket
import Pyro4.naming
import time
import sys
from concurrent.futures import ThreadPoolExecutor
import re

class Person(Thread):

    def __init__(self, id, n_items, goods, role, ns_name, hmac_key, haskey):
        """
        :param id: unique id for the person. The format is buyer1@hostname, seller0@hostname, seller1@hostname
        :param n_items: number of items a seller has, irrelevant field if a person is assigned as a buyer
        :param goods: all goods allowed in the market
        :param role: the person's role
        :param ns_name: name server host name
        :param hmac_key: hmac key for private connection
        """
        Thread.__init__(self)
        self.id = id
        self.max_items = n_items

        self.itemlock = Lock()
        self.n_items = n_items

        self.goods = goods
        self.good = self.pick_random_item(goods)
        self.role = role
        
        self.hmac = hmac_key if haskey else None
        self.ns = self.get_nameserver(ns_name, self.hmac)
        self.hostname = socket.gethostname()

        self.neighbors_lock = Lock()
        self.neighbors = {}

        self.seller_list_lock = Lock()
        self.sellers = []
        self.executor = ThreadPoolExecutor(max_workers = 10)

        

    def get_random_neighbors(self, ns_dict):
        """
        This function takes the dictionary obtained from a name server and filters out
        the thread itself
        :param ns_dict: a dictionary name-to-URI from a name server
        :return:
        """
        list = []

        # Find peers with the same hostname
        re_pattern = "seller[0-9]+@.|buyer[0-9]+@."
        for id in ns_dict:
            if "NameServer" not in id and self.id != id and re.match(re_pattern, id) and self.hostname in id:
                list.append(id)

        self.sayhi2neighbor(list)

        list.clear()
        # Find peers with different hostname
        for id in ns_dict:
            if "NameServer" not in id and self.id != id and re.match(re_pattern, id) and self.hostname not in id:
                list.append(id)
            
        self.sayhi2neighbor(list)
    def sayhi2neighbor(self, list):

        # Randomly pick one neighbor
        if list:
            random_neighbor_id = list[random.randint(0, len(list) - 1)]

            self.neighbors[random_neighbor_id] = self.ns.lookup(random_neighbor_id)

            with Pyro4.Proxy(self.neighbors[random_neighbor_id]) as neigbor:
                neigbor._pyroHmacKey = self.hmac
                # send a message to the neighbor
                try:
                    self.executor.submit(neigbor.sayhi, self.id)

                except(Exception) as e:
                    # If this peer can't be contacted, decrement its active point
                    template = "An exception of type {0} occurred at get_random_neighbor. Arguments:\n{1!r}"
                    message = template.format(type(e).__name__, e.args)
                    print(message)


    @Pyro4.expose
    def sayhi(self, peer_id):
        """
        This function is used to establish mutual connection
        :param peer_id:
        :return:
        """
        with self.neighbors_lock:

            if peer_id not in self.neighbors:
                self.neighbors[peer_id] = self.ns.lookup(peer_id)

    def get_nameserver(self, ns_name, hmac_key):

        try:
            ns = Pyro4.locateNS(host = ns_name, hmac_key = hmac_key)
            return ns
        except Exception as e:
            template = "An exception of type {0} occurred at get_nameserver. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)


    def run(self):

        try:

            with Pyro4.Daemon(host = self.hostname) as daemon:
                daemon._pyroHmacKey = self.hmac
                person_uri = daemon.register(self)
                self.ns.register(self.id, person_uri)

                if self.role == "buyer":
                    print(self.id, "joins market buying", self.good)
                else:
                    print(self.id, "joins market selling", self.good)

                # Start accepting incoming requests
                self.executor.submit(daemon.requestLoop)
                self.get_random_neighbors(self.ns.list())


                #Buyer loop
                while True and self.role == "buyer":

                    with self.neighbors_lock:
                        if self.neighbors:
                            for neighbor_location in self.neighbors:
                                print(self.id,"has a neighbor", neighbor_location)

                                with Pyro4.Proxy(self.ns.lookup(neighbor_location)) as neighbor:
                                    neighbor._pyroHmacKey = self.hmac
                                    id_list = [self.id]
                                    self.executor.submit(neighbor.lookup, self.good, 5, id_list)

                            time.sleep(0.5)
                #Seller loop
                while True:
                    with self.neighbors_lock:
                        if self.neighbors:
                            for n in self.neighbors:
                                print(self.id, "has a neighbor", n)
                    time.sleep(0.5)
        except(Exception) as e:
            template = "An exception of type {0} occurred at run. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)

    @Pyro4.expose
    def lookup(self, product_name, hopcount, id_list):
        """
        This procedure should search the network; all matching sellers respond to this message with their IDs.
        The hopcount is decremented at each hop and the message is discarded when it reaches 0.

        :param product_name: Name of the product buyer wants
        :param hopcount: Max number of hops allowed to reach the seller
        :id_list: an id list used to traverse back to original sender
        :return: The sellers who sell specified product
        """
        hopcount -= 1

        if hopcount <= 0:
            print("Max number of hop reached, message is discarded")
            return

        incoming_peer_id = id_list[-1]
        print(incoming_peer_id, "asks", self.id, "about", product_name)

        try:

            # Matching seller
            if self.role == "seller" and product_name == self.good and self.n_items > -1:

                with Pyro4.Proxy(self.ns.lookup(incoming_peer_id)) as recipient:
                    recipient._pyroHmacKey = self.hmac
                    # Matching seller appends its id to the head of the list so it is received at the original request sender
                    id_list.pop()
                    id_list.insert(0, self.id)
                    self.executor.submit(recipient.reply, self.id, id_list)
                    print(self.id, "replies to", incoming_peer_id, "about", product_name)

            # Anyone else who is not a matching seller simply forwards the messages
            else:
                for neighbor_location in self.neighbors:
                    # Don't ask the peer who just asked you
                    if neighbor_location != incoming_peer_id:
                        with Pyro4.Proxy(self.neighbors[neighbor_location]) as neighbor:
                            neighbor._pyroHmacKey = self.hmac
                            id_list.append(self.id)
                            self.executor.submit(neighbor.lookup, product_name, hopcount, id_list)


        except(Exception) as e:
            template = "An exception of type {0} occurred at Lookup. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)


    @Pyro4.expose
    def reply(self, peer_id,  id_list):
        """
        This is a reply message with the peerID of the seller
        :param peer_id: peer who responds
        :param id_list: a list of id used to traverse back to original sender
        :return:
        """
        try:
            if id_list and len(id_list) == 1:
                # Only one peer id left, this is the seller_id by current design

                print(self.id, "got a reply from", peer_id)

                with self.seller_list_lock:
                    self.sellers.extend(id_list)
                    random_seller_id = self.sellers[random.randint(0, len(self.sellers) - 1)]

                with Pyro4.Proxy(self.ns.lookup(random_seller_id)) as seller:
                    seller._pyroHmacKey = self.hmac
                    future = self.executor.submit(seller.buy, self.id)

                with self.seller_list_lock:

                    if future.result():
                        print(self.id, "purchased", self.good, "from", random_seller_id)
                        self.sellers = []
            elif id_list and len(id_list) > 1:
                print(self.id, "got a reply from", peer_id)
                recipient_id = id_list.pop()
                with Pyro4.Proxy(self.neighbors[recipient_id]) as recipient:
                    recipient._pyroHmacKey = self.hmac
                    self.executor.submit(recipient.reply, self.id, id_list)

        except(Exception) as e:
            template = "An exception of type {0} occurred at Reply. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)
            sys.exit()

    @Pyro4.expose
    def buy(self, peer_id):

        with self.itemlock:
            if self.n_items > 0:
                self.n_items -= 1
                print(peer_id, "purchased", self.good)
                return True
            # No more items to sell, randomly pick up another item
            else:
                print(peer_id, "failed to purchase", self.good)
                self.good = self.pick_random_item(self.goods)
                self.n_items = self.max_items
                print(self.id, "now sells", self.good)

    def pick_random_item(self, goods):
        """
        :param goods: list of possible goods to sell or buy
        :return: a randomly picked good
        """

        return goods[random.randint(0, len(goods) -1)]
