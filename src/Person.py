import Pyro4
import random
import configparser
from threading import Thread, Lock
import socket
import Pyro4.naming
import time
import sys
import copy

class Person(Thread):

    def __init__(self, id, n_items, goods, role, known_hostnames):
        """
        :param id: unique id for the person. The format is buyer1@hostname, seller0@hostname, seller1@hostname
        :param n_items: number of items a seller has, irrelevant field if a person is assigned as a buyer
        :param goods: all goods allowed in the market
        :param role: the person's role
        :param known_hostnames: all known hostname for the initialization of the network
        """
        Thread.__init__(self)
        self.id = id
        self.n_items = n_items
        self.goods = goods
        self.good = goods #goods[random.randint(0, len(goods) - 1)]
        self.role = role
        self.known_hosts = known_hostnames
        self.neighbors = {}
        self.itemlock = Lock()
        self.seller_lock = Lock()
        self.ns = Pyro4.locateNS()
        self.sellers = []

    def get_radom_neighbors(self, ns_dict):
        """
        This function takes the dictionary obtained from a name server and filters out
        the thread itself
        :param ns_dict: a dictionary name-to-URI from a name server
        :return:
        """
        list = []
        # Filters out the NameServer and itself from the registered objects. Only store the actual location of
        # other registered objects
        for id in ns_dict:
            if "NameServer" not in id and self.id != id:
                list.append(id)

        # Randomly pick one neighbor. The number 10 is used to keep the number of times the neighbor responds
        # or contacts
        if list:
            self.neighbors[list[random.randint(0, len(list) - 1)]] = 10

    def run(self):
        hostname = socket.gethostname()


        with Pyro4.Daemon() as daemon:
            person_uri = daemon.register(self)
            self.ns.register(self.id, person_uri)
            self.get_radom_neighbors(self.ns.list())

            # for ns_hostname in self.known_hosts :
            #     try:
            #         with Pyro4.locateNS(host=ns_hostname) as ns:
            #             person_uri = daemon.register(self)
            #             ns.register(self.id, person_uri)
            #
            #     except(Exception) as e:
            #         template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            #         message = template.format(type(e).__name__, e.args)
            #         print(message)

            print(self.id, "join market")

            t = Thread(target=daemon.requestLoop)
            t.start()

            #Buyer loop
            while True and self.role == "buyer":

                if self.neighbors:
                    for neighbor_location in self.neighbors:
                        print("my neigbor is", neighbor_location)
                        try:
                            neighbor = Pyro4.Proxy(self.ns.lookup(neighbor_location))
                            id_list = [self.id]
                            Thread(target = neighbor.lookup, args=(self.good, 4, id_list)).start()
                            # neighbor.lookup(self.good, 4, id_list)

                        except(Exception) as e:
                            # If this peer can't be contacted, decrement its active point
                            self.neighbors[neighbor_location] -= 1
                            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                            message = template.format(type(e).__name__, e.args)
                            print(message)
                    time.sleep(1)

            #Seller loop
            while True:
                time.sleep(1)


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
        incoming_peer_id = id_list[-1]
        print(incoming_peer_id, "asks about", product_name)

        # When getting contacted by a peer, add the peer to active neighbor list (Unfinished feature)
        if incoming_peer_id in self.neighbors and self.neighbors[incoming_peer_id] < sys.maxsize:
            self.neighbors[incoming_peer_id] += 1
        else:
            self.neighbors[incoming_peer_id] = 10

        self.itemlock.acquire()
        if self.role == "seller" and product_name == self.good:

            if self.n_items > 0:
                try:
                    print("selling to", incoming_peer_id)
                    recipient = Pyro4.Proxy(self.ns.lookup(incoming_peer_id))
                    id_list.pop()
                    id_list.insert(0, self.id)
                    Thread(target = recipient.reply, args = (id_list,)).start()

                except(Exception) as e:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(e).__name__, e.args)
                    print(message)
                    sys.exit()

        self.itemlock.release()

        # else:
        #     if self.neighbors:
        #         for neighbor_location in self.neighbors:
        #             neighbor = Pyro4.Proxy(self.ns.lookup(neighbor_location))
        #             neighbor.lookup(self.good, hopcount, self.id)



    @Pyro4.expose
    def reply(self, id_list):
        """
        This is a reply message with the peerID of the seller
        :param peer_id: peer who responds
        :param id_list: a list of id used to traverse back to original sender
        :return:
        """
        if id_list:
            # Only one peer id left, this is the seller_id by current design
            if len(id_list) == 1:

                print("I got a reply from", id_list)
                print(self.seller_lock.locked())
                self.seller_lock.acquire()
                self.sellers.extend(id_list)
                random_seller_id = self.sellers[random.randint(0, len(self.sellers) - 1)]
                self.seller_lock.release()

                seller = Pyro4.Proxy(self.ns.lookup(random_seller_id))
                print("purchasing")
                basket = []
                t = Thread(target = seller.buy, args = (self.id, basket,))
                t.start()
                self.seller_lock.acquire()
                if basket:
                    self.sellers = []
                self.seller_lock.release()

    @Pyro4.expose
    def buy(self, peer_id, basket):
        print(self.itemlock.locked())

        self.itemlock.acquire()
        if self.n_items > 0:
            print(peer_id, "purchased", self.good)
            self.n_items -= 1
            basket.append(self.good)
        else:
            print(peer_id, "failed to purchase", self.good)

        self.itemlock.release()











