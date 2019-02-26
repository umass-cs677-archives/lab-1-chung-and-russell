import configparser

class MakePeople:

    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config")
        print(config['DEFAULT']['N'])


