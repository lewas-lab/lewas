import os, ConfigParser

__all__ = [ 'parsers','models' ]

def getsite(config):
    c = ConfigParser.RawConfigParser()
    c.read(os.path.abspath(config))
    return c.get("main", "site")
