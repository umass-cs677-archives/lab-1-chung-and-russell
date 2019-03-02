import Pyro4
import random
import configparser
from threading import Lock, Thread
import socket
import Pyro4.naming
import time

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
        self.good = goods[random.randint(0, len(goods) - 1)]
        self.role = role
        self.known_hosts = known_hostnames
        self.neighbors = {}

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
        self.neighbors[list[random.randint(0, len(list) - 1)]] = 10

    def run(self):
        hostname = socket.gethostname()


        with Pyro4.Daemon() as daemon:
            ns = Pyro4.locateNS()
            person_uri = daemon.register(self)
            ns.register(self.id, person_uri)
            self.get_radom_neighbors(ns.list())

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

            #Buyer loop
            while True and self.role == "buyer":
                #
                # print(self.id)
                # for neighbor_location in self.neighbors:
                #
                #     try:
                #         neighbor = Pyro4.Proxy(ns.lookup(neighbor_location))
                #         neighbor.lookup(self.good, 4, self.id)
                #
                #     except(Exception) as e:
                #         self.neighbors[neighbor_location] -= 1
                #         if self.neighbors[neighbor_location] <= 0:
                #             del self.neighbors[neighbor_location]
                #         template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                #         message = template.format(type(e).__name__, e.args)
                #         print(message)
                # time.sleep(3)
                continue
            while True and self.role == "seller":
                daemon.requestLoop()



    @Pyro4.expose
    def lookup(self, product_name, hopcount, id):
        """
        This procedure should search the network; all matching sellers respond to this message with their IDs.
        The hopcount is decremented at each hop and the message is discarded when it reaches 0.

        :param product_name: Name of the product buyer wants
        :param hopcount: Max number of hops allowed to reach the seller
        :return: The sellers who sell specified product
        """

        print(id, "has a look up from", self.id)
    @Pyro4.expose
    def reply(self, seller_id):
        """
        This is a reply message with the peerID of the seller
        :param seller_id:
        :return:
        """
        print("hi")
        return

    @Pyro4.expose
    def buy(self, peer_id):

        return

    @Pyro4.expose
    def hi(self):
        print("hi")






