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
import subprocess


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
        # locate specific nameserver
        self.ns = Pyro4.locateNS(host = IP_ADDRESS, port = PORT, hmac_key = HMAC_KEY)
        self.id_list, self.uri_list = get_ns_peer_list(self.ns)
        self.test_buyer = Person('testbuyer@' + socket.gethostname(), 10, ['FISH','SALT','BOARS'], 'BUYER', ' ', self.ns)
        self.test_seller = Person('testseller@' + socket.gethostname(), 10, ['FISH','SALT','BOARS'], 'SELLER', ' ', self.ns)
        self.diff_machine_peer_ids = []
        for peer_id in self.id_list:
            peer_hostname = peer_id.split('@')[1]
            if socket.gethostname() != peer_hostname:
                self.diff_machine_peer_ids.append(peer_id)
        

    def test_local_interaction(self):
        # make sure newly spawn test seller and buyer can interact with each other on same machine
        # interact function just returns the id of the peer that was called
        self.assertEqual( self.test_buyer.interact(self.test_seller),self.test_seller.id)
 
    def test_nonlocal_machines_registered(self):
        self.assertTrue(len(self.diff_machine_peer_ids)>0)
        
    def test_cross_machine_interaction(self):
        # look for peer on a different machine
        # make sure interaction is possible
        for nonlocal_id in self.diff_machine_peer_ids:
            peer_proxy = Pyro4.Proxy(self.ns.lookup(nonlocal_id))
            self.test_buyer.interact(peer_proxy)
            self.test_seller.interact(peer_proxy)
                
        
    def tearDown(self):
        pass
 
if __name__ == '__main__':
    subprocess.call('./name_server.sh')
    unittest.main()