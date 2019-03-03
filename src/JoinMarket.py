import configparser
from Person import Person
import Pyro4
import Pyro4.naming
import re
import socket
import random
import sys

def get_people(config):
    n = int(config["DEFAULT"]["N_PEOPLE"])
    roles = re.split(",\s*", config["DEFAULT"]["ROLES"])
    goods = sys.argv[3]#re.split(",\s*", config["DEFAULT"]["GOODS"])
    known_hostnames = re.split(",\s*", config["NETWORK_INFO"]["KNOWN_HOSTS"])
    people = []

    for i in range(n):
        role = sys.argv[1]#roles[random.randint(0,len(roles) - 1)]
        id = sys.argv[2] + "@" + socket.gethostname()# + str(i) + "@" + socket.gethostname()
        n_items = int(config["DEFAULT"]["N_ITENS"])
        person = Person(id, n_items, goods, role, known_hostnames)
        people.append(person)

    return people


if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read("config")

    people = get_people(config)

    for person in people:
        person.start()






