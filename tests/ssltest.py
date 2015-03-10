#!/usr/bin/env python2

import sys, re
sys.path.append('../')
import lewas.models
from lewas.parsers import split_parser, field_rangler
import lewas.datastores

class SSLTest(lewas.models.Instrument):
    fields = [ field_rangler((int, 'test', 'ssl', 'certs')) ]
    parsers = { r'([0-9]+)': lewas.parsers.split_parser(delim=' ',fields=fields) }
      
if __name__ == '__main__':
    datastream = sys.stdin
    config = '../config.ssltest'

    config = lewas.readConfig(config)
    datastore = lewas.datastores.leapi(config)
        
    ssltest = SSLTest(datastream, config.site)
    ssltest.run(datastore)
