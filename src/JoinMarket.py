import configparser
from Person import Person
from threading import Thread
import Pyro4.naming
import re
import socket
import random
import sys

def get_people(config):
    n = int(config["DEFAULT"]["N_PEOPLE"])
    roles = re.split(",\s*", config["DEFAULT"]["ROLES"])
    goods = re.split(",\s*", config["DEFAULT"]["GOODS"])
    ns_name = sys.argv[1]
    people = []
    hmac_key = config["NETWORK_INFO"]["HMAC_KEY"]

    # Starts name server
    try:
        ns = Pyro4.locateNS(host = ns_name)
    except Exception:
        print("No server found, start one")
        # Thread(target=Pyro4.naming.startNSloop, kwargs={"host": ns_name, "hmac": hmac_key}).start()
        Thread(target=Pyro4.naming.startNSloop, kwargs={"host": ns_name}).start()
        # haskey = True

    # Future implementation may include hmac key for security
    haskey = False

    for i in range(n):
        role = roles[random.randint(0,len(roles) - 1)]
        id = role + str(i) + "@" + socket.gethostname()
        n_items = int(config["DEFAULT"]["N_ITENS"])
        person = Person(id, n_items, goods, role, ns_name, hmac_key, haskey)
        people.append(person)

    return people


if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read("config")

    people = get_people(config)

    try:
        for person in people:
            person.start()
    except KeyboardInterrupt:
        sys.exit()






