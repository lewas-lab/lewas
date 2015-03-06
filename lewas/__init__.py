import os, ConfigParser
from config import Config

__all__ = [ 'parsers','models' ]

def readConfig(config="../config.example"):
    return Config(config)

def getsite(config):
    c = ConfigParser.RawConfigParser()
    c.read(os.path.abspath(config))
    return c.get("main", "site")
