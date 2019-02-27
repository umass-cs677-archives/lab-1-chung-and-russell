import configparser
from src.Person import Person
import Pyro4
import re

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

    with Pyro4.Daemon() as daemon:
        person_uri = daemon.register(person)
        print(daemon.uriFor("BUYER1", nat=False))
        print(daemon.uriFor("BUYER1", nat=False))
    for hostname in known_hostnames:
        try:
            with Pyro4.locateNS(host = hostname) as ns:
                ns.register(id, person_uri)
                print(id, "joined the market")
                daemon.requestLoop()
        except:
            print("no name server at hostname:", hostname)





