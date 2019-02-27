import configparser
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
    people = []

    for i in range(n):
        role = roles[random.randint(0,len(roles) - 1)]
        id = role + str(i) + "@" + socket.gethostname()
        n_items = config["DEFAULT"]["N_ITENS"]
        person = Person(id, n_items, goods, role)
        people.append(person)

    return people

if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read("config")

    known_hostnames = re.split(",\s*", config["NETWORK_INFO"]["KNOWN_HOSTS"])

    hostname = socket.gethostname()

    with Pyro4.Daemon(host = hostname) as daemon:
        people_uri = {}
        people = get_people(config)

        for person in people:
            person_uri = daemon.register(person)
            people_uri[person.id] = person_uri

        for ns_hostname in known_hostnames:
            try:
                with Pyro4.locateNS(host=ns_hostname) as ns:

                    for person_uri in people_uri:
                        ns.register(person_uri, people_uri[person_uri])
                        print(person_uri, "joined the market")

                    daemon.requestLoop()
            except(Exception) as e:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(e).__name__, e.args)
                print(message)







