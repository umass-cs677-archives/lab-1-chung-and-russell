# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 02:03:49 2019

@author: Russell Lee
"""

#testing requires nameserver to already have registered peers on different machines
#TODO: have unit test setup be finished with setUp() functions

IP_ADDRESS = '128.119.243.168'
PORT = 9090
HMAC_KEY = 'cs677'

N_ITENS = 10
GOODS = 'FISH,SALT,BOARS'
ROLES = 'BUYER, SELLER'

import unittest
import Pyro4
from . import Person
import socket


def get_ns_peer_list(nameserver):
    ns_dict = nameserver.list()
    peer_list = []
    uri_list = []
    for (key,val) in zip(ns_dict,ns_dict.values()):
        if "NameServer" not in key:
            peer_list.append(key)
            uri_list.append(val)
    return peer_list,uri_list

class testP2P(unittest.TestCase):
 
    def setUp(self):
        self.ns = Pyro4.locateNS(host = IP_ADDRESS, port = PORT, hmac_key = HMAC_KEY)
        self.id_list, self.uri_list = get_ns_peer_list(self.ns)
        self.test_buyer = Person('testbuyer@' + socket.gethostname(), 10, ['FISH','SALT','BOARS'], 'BUYER', ' ', self.ns)
        self.test_seller = Person('testseller@' + socket.gethostname(), 10, ['FISH','SALT','BOARS'], 'SELLER', ' ', self.ns)

    def test_daemon_register(self):
        self.assertEqual( 3*4, 12)
 
    def test_strings_a_3(self):
        self.assertEqual( 'a'*3, 'aaa')
        
    def tearDown()
 
if __name__ == '__main__':
    unittest.main()