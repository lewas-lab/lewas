import logging
from os.path import splitext
import re

from sources import fileSource
from lewas import readConfig
from lewas.exceptions import NoParserDefined
from lewas.sources import serialSource

logger = logging.getLogger(__name__)

def importModule(module):
    pkg, module = splitext(module)
    module = module.strip('.')
    _store = __import__(pkg, fromlist = [ module ])
    logger.log(logging.INFO, 'importing {} from {}'.format(module, _store)) 
    return getattr(_store, module, None)

def datasource(name, config):
    logger.log(logging.INFO, 'creating datasource for {}'.format(name))
    if 'baud' in config:
        kwargs = {k: v for k,v in config.items() if k in ['xonxoff','timeout']}
        return serialSource(config, **kwargs)

    if 'datasource' in config:
        return importModule(config['datasource'])(config)

    return importModule(name + '.datasource')(config)

def getDatastore(args, config):
    return importModule(config.datastore['module'])(**config.datastore)

def getReader(args, config):
    if args.file:
        logger.log(logging.INFO, 'using filesource with {}'.format(args.file))
        return fileSource(args.file, delay=config.get('read_delay', 0))
    else:
        return datasource(args.name, config)

def getNamedModule(name, args, config):
    nm = importModule(config.get(name, args.name  + '.' + name))
    if nm is not None:
        logger.log(logging.DEBUG, 'returning module {}({})'.format(name, args))
        return nm(args)
    return None

def make_re(str_or_re):
    if hasattr(str_or_re, 'match'):
        return str_or_re
    return re.compile(str_or_re)

class ParsedCli():
    def __init__(self, args, config):
        self.args = args
        self.name = args.name
        self.config = getattr(config, self.name)
        if 'site' not in self.config:
            self.config['site'] = config.site
        self.reader = getReader(args, self.config)
        try:
            getattr(__import__(args.name), 'init')(self)
        except AttributeError as e:
            pass # no init method
        self.parser = getNamedModule('parser', self, self.config)
        # parsers can either be:
        # - a callable
        # - a list of callables
        # - a dict where keys are regular expressions and values are callables
        if hasattr(self.parser, 'items'):
            self.parser = { make_re(k): p for k,p in self.parser.items() }
            
        self.datastore = getDatastore(self, config)
 
    @property
    def instrument_name(self):
        return self.config.get('name', self.args.name)

def parse(*args, **kwargs):
    import argparse
    from os.path import basename
    from sys import argv

    logger.log(logging.DEBUG, 'parse with args={}, kwargs={}'.format(args, kwargs))
    parser = argparse.ArgumentParser(description='LEWAS Sensor controller')
    parser.add_argument('-c', '--config', default='./config', help='configuration file')
    parser.add_argument('-n', '--name', default=kwargs.pop('name', basename(argv[0])), help='name of sensor')
    parser.add_argument('-f', '--file', help='data file to read from instead of source')
    parser.add_argument('-v', '--verbosity', action='count', help='increase output verbosity')
    args = parser.parse_args()

    config = readConfig(args.config)
    return ParsedCli(args, config)


