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

    hostname = socket.gethostname()

    with Pyro4.Daemon(host = hostname) as daemon:
        person_uri = daemon.register(person)

        for hostname in known_hostnames:
            try:
                with Pyro4.locateNS(host=hostname) as ns:
                    ns.register(id, person_uri)
                    print(id, "joined the market")
                    daemon.requestLoop()
            except(Exception) as e:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(e).__name__, e.args)
                print(message)








