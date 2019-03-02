import Pyro4
import random
import configparser


class Person(object):

    def __init__(self, id, n_items, goods, role):

        self.id = id
        self.n_items = n_items
        self.good = goods[random.randint(0, len(goods) - 1)]
        self.role = role

    def get_neighbors(self, neighbors):

        self.neighbors = neighbors

    @Pyro4.expose
    def lookup(self, product_name, hopcount):
        """
        This procedure should search the network; all matching sellers respond to this message with their IDs.
        The hopcount is decremented at each hop and the message is discarded when it reaches 0.

        :param product_name: Name of the product buyer wants
        :param hopcount: Max number of hops allowed to reach the seller
        :return: The sellers who sell specified product
        """

        return

    @Pyro4.expose
    def reply(self, seller_id):
        """
        This is a reply message with the peerID of the seller
        :param seller_id:
        :return:
        """

        return

    @Pyro4.expose
    def buy(self, peer_id):

        return


    def start_trading(self):

        if self.isbuyer:
            print("")


        else:
            while True:
                n_goods = len(self.goods)
                product_name = self.goods[random.randint(n_goods)]

                for neighbor in self.neighbors:
                    neighbor.lookup(product_name, 4)





