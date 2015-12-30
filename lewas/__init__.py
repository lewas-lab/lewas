import os, ConfigParser
from config import Config
import logging

__all__ = [ 'parsers', 'models', 'stores' ]

logger = logging.getLogger(__name__)

def readConfig(config="../config.example"):
    return Config(config)

def getsite(config):
    c = ConfigParser.RawConfigParser()
    c.read(os.path.abspath(config))
    return c.get("main", "site")


