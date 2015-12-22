import logging
from os.path import splitext

from sources import fileSource
from lewas import readConfig
from lewas.exceptions import NoParserDefined
from lewas.sources import serialSource

def importModule(module):
    pkg, module = splitext(module)
    module = module.strip('.')
    _store = __import__(pkg, fromlist = [ module ])
    logging.info('importing {} from {}'.format(module, _store)) 
    return getattr(_store, module)

def datasource(name, config):
    logging.info('creating datasource for {}'.format(name))
    if 'baud' in config:
        kwargs = {k: v for k,v in config.items() if k in ['xonxoff','timeout']}
        return serialSource(config, **kwargs)

    if 'datasource' in config:
        return importModule(config['datasource'])

    return importModule(name + '.datasource')

def getDatastore(args, config):
    return importModule(config.datastore['module'])(**config.datastore)

def getReader(args, config):
    if args.file:
        logging.info('using filesource with {}'.format(args.file))
        return fileSource(args.file, delay=1)
    else:
        return datasource(args.name, config)

def getParser(args, config):
    return importModule(config.get('parser', args.name  + '.parser'))(args)

class ParsedCli():
    def __init__(self, args, config):
        self.args = args
        self.name = args.name
        self.config = getattr(config, self.name)
        if 'site' not in self.config:
            self.config['site'] = config.site
        self.reader = getReader(args, self.config)
        getattr(__import__(args.name), 'init')(self)
        self.parser = getParser(self, self.config)
        self.tokenizer = importModule(self.config.get('tokenizer', self.name + '.tokenizer'))
            
        self.datastore = getDatastore(self, config)
 
    @property
    def instrument_name(self):
        return self.config.get('name', self.args.name)

def parse(*args, **kwargs):
    import argparse
    from os.path import basename
    from sys import argv

    parser = argparse.ArgumentParser(description='LEWAS Sensor controller')
    parser.add_argument('-c', '--config', default='./config', help='configuration file')
    parser.add_argument('-n', '--name', default=kwargs.pop('name', basename(argv[0])), help='name of sensor')
    parser.add_argument('-f', '--file', help='data file to read from instead of source')
    args = parser.parse_args()

    config = readConfig(args.config)
    return ParsedCli(args, config)


