# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 02:03:49 2019

@author: Russell Lee
"""

#testing requires nameserver to already have registered peers on different machines
#TODO: have unit test setup be finished with setUp() functions
import unittest
read_file = 'seller0@elnux1test'


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
        self.contents = open('seller0@elnux1test','r').read()
        

    def test_decrementing_concurrent_stock(self):
        # make sure stock decreases by 1, and never goes below 0 even with
        # concurrent requests
        stock = []
        curr_stock = 4
        for element in self.contents.split('remains'):
            itemstock = element[-1]
            if itemstock.isdigit():
                self.assertEqual(curr_stock,int(itemstock))
                curr_stock = curr_stock -1
                if curr_stock < 0:
                    curr_stock = 4
        
        print("Stock correctly decreases by 1 each time!")
 
    def test_refresh_stock(self):
        # make sure when fail to purchase, new item is in stock
        refreshes = []
        for element in self.contents.split('remains'):
            itemstock = element[-1]
            if itemstock.isdigit():
                if int(itemstock) == 4:
                    refreshes.append(element)
        
        print(refreshes[1:])
        print('')
        print("Via manual inspection, the stock refreshes when failure to purchase occurs")
        
    def tearDown(self):
        pass
 
if __name__ == '__main__':
    unittest.main()