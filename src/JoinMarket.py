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
    ids = []

    for i in range(n):
        role = roles[random.randint(0,len(roles) - 1)]
        id = "peer" + str(i) + "@" + socket.gethostname()
        n_items = config["DEFAULT"]["N_ITENS"]
        person = Person(id, n_items, goods, role)
        neighbors = [int(idx_string) for idx_string in re.split(",\s*", config["NEIGHBOR_INFO"][str(i)])]
        person.get_neighbors(neighbors)
        people.append(person)
        ids.append(id)

    return people,ids

# def get_random_neighbor(neighbors, n):


if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read("config")

    known_hostnames = re.split(",\s*", config["NETWORK_INFO"]["KNOWN_HOSTS"])

    hostname = socket.gethostname()

    with Pyro4.Daemon(host = hostname) as daemon:
        people_uri = {}
        people,_ = get_people(config)

        for person in people:
            person_uri = daemon.register(person)
            people_uri[person.id] = person_uri

        try:
            #looks up a specific nameserver from config file
            #requires nameserver to be manually setup
            #TODO: set this up so TAs will be able to run our code?
            ip_address = config["NETWORK_INFO"]["IP_ADDRESS"]
            port = int(config["NETWORK_INFO"]["PORT"])
            hmac_key = config["NETWORK_INFO"]["HMAC_KEY"]
            
            with Pyro4.locateNS(host = ip_address, port = port, hmac_key = hmac_key) as ns:

                for person_uri in people_uri:
                    ns.register(person_uri, people_uri[person_uri])
                    print(person_uri, "joined the market")

                daemon.requestLoop()
        except(Exception) as e:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)







