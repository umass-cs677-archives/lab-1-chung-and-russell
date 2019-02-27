import configparser
from Person import Person
import Pyro4
import Pyro4.naming
import re
import socket

if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read("config")

    known_hostnames = re.split(",\s*", config["NETWORK_INFO"]["KNOWN_HOSTS"])
    id = config["DEFAULT"]["ID"]
    isbuyer = config["DEFAULT"].getboolean("ISBUYER")

    if isbuyer:
        n_items = 0
    else:
        n_items = config["DEFAULT"]["N_ITENS"]
    goods = re.split(",\s*",config["DEFAULT"]["GOODS"])

    person = Person(id, n_items, goods ,isbuyer)

    name_server_hostname = config["NETWORK_INFO"]["NAME_SERVER_HOST"]
    hostname = socket.gethostname()
    # Pyro4.naming.startNS(host = name_server_hostname)

    with Pyro4.Daemon(host = hostname) as daemon:
        person_uri = daemon.register(person)
        print(daemon.uriFor("BUYER1", nat=False))
        print(daemon.uriFor("BUYER1", nat=False))

        with Pyro4.locateNS(host=name_server_hostname) as ns:
            ns.register(id, person_uri)
            print(id, "joined the market")
            daemon.requestLoop()






