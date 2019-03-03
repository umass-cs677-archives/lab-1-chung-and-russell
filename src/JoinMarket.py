# edlab machines do not have configparser file
# therefore, temporarily hardcoding variable from config until resolved

N_PEOPLE = 6
N_ITENS = 10
GOODS = 'FISH,SALT,BOARS'
ROLES = 'BUYER, SELLER'

IP_ADDRESS = '128.119.243.168'
PORT = 9090
HMAC_KEY = 'cs677'
KNOWN_HOSTS = 'elnux1.cs.umass.edu, elnux2.cs.umass.edu, elnux3.cs.umass.edu, elnux7.cs.umass.edu'


#import configparser
from Person import Person
import Pyro4
import Pyro4.naming
import re
import socket
import random

def get_people(config):
    n = int(config["DEFAULT"]["N_PEOPLE"])
    roles = re.split(",\s*", config["DEFAULT"]["ROLES"])
    goods = re.split(",\s*", config["DEFAULT"]["GOODS"])
    known_hostnames = re.split(",\s*", config["NETWORK_INFO"]["KNOWN_HOSTS"])
    ip_address = config["NETWORK_INFO"]["IP_ADDRESS"]
    port = int(config["NETWORK_INFO"]["PORT"])
    hmac_key = config["NETWORK_INFO"]["HMAC_KEY"]
    nameserver = Pyro4.locateNS(host = ip_address, port = port, hmac_key = hmac_key)
    people = []
    ids = []
    for i in range(n):
        role = roles[random.randint(0,len(roles) - 1)]
        id = "peer" + str(i) + "@" + socket.gethostname()
        n_items = config["DEFAULT"]["N_ITENS"]
        person = Person(id, n_items, goods, role, known_hostnames,nameserver)
        people.append(person)
        ids.append(id)

    return people,ids,nameserver

def get_people_simple():
    n = N_PEOPLE
    roles = re.split(",\s*", ROLES)
    goods = re.split(",\s*", GOODS)
    known_hostnames = re.split(",\s*", KNOWN_HOSTS)
    ip_address = IP_ADDRESS
    port = PORT
    hmac_key = HMAC_KEY
    nameserver = Pyro4.locateNS(host = ip_address, port = port, hmac_key = hmac_key)
    people = []
    ids = []
    for i in range(n):
        role = roles[random.randint(0,len(roles) - 1)]
        id = "peer" + str(i) + "@" + socket.gethostname()
        n_items = N_ITENS
        person = Person(id, n_items, goods, role, known_hostnames,nameserver)
        people.append(person)
        ids.append(id)

    return people,ids,nameserver
# def get_random_neighbor(neighbors, n):
    
def get_ns_peer_list(nameserver):
    ns_dict = nameserver.list()
    peer_list = []
    uri_list = []
    for (key,val) in zip(ns_dict,ns_dict.values()):
        if "NameServer" not in key:
            peer_list.append(key)
            uri_list.append(val)
    return peer_list,uri_list

def get_roundrobin_neighbors(nameserver):
    peer_list,uri_list = get_ns_peer_list(nameserver)
    pass
    

if __name__ == "__main__":

#    config = configparser.ConfigParser()
#    config.read("config")
    
    people,ids,ns = get_people_simple()
    for person in people:
        person.register()
    
    peer_list,uri_list = get_ns_peer_list(ns)
    
    
    for person in people:
        person.set_roundrobin_neighbors(peer_list)
        #person.run()







