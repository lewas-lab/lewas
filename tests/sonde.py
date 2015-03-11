#!/usr/bin/env python2

import sys
sys.path.append('../')

## What is clearer, a class structure

import re
import lewas.models
import lewas.parsers
import lewas.datastores

# NOTE: fields and field order are determined by the configuration of
# the Sonde and are not necessarily constant. Eventually we should add
# a getHeaders() function that retreives and parses the column header
# from the Sonde. To do that, send three space characters, wait for
# H?:, send 'H', read two lines, those should be the headers

sonde_fields = [ (str, 'time', 'HHMMSS', None),
               (float, 'water', 'temperature','C'),
               (float, 'water', 'pH','pH'),
               (float, 'water', 'specific conductance', 'mS/cm'),
               (float, 'water', 'depth', 'm'),
               (float, 'water', 'LDO%', '%'),
               (float, 'water', 'dissolved oxygen', 'mg/l'),
               (float, 'water', 'turbidity', 'NTU'),
               (float, 'water', 'Redox potential', 'mV'),
               (float, 'battery', 'voltage', 'V')
               ]

class Sonde(lewas.models.Instrument):
    fields = [ lewas.parsers.UnitParser(t,(mm,mn),u) for t,mm,mn,u in sonde_fields ]
    parsers = { r'(.*)': lewas.parsers.split_parser(delim=' ',fields=fields) }
            
    def start(self):
        pass
        
if __name__ == '__main__':
    timeout=0
    if len(sys.argv) == 1:
        datastream = open("sonde_data.txt", "r")
        config = '../config.example'
    else:
        import serial
        timeout=1
        datastream = serial.Serial("/dev/tty{}".format(sys.argv[1]), 19200, xonxoff=0,timeout=timeout) #argv[1] e.g. USB0
        config = '../config'

    config = lewas.readConfig(config)
    datastore = lewas.datastores.leapi(config)
        
    sonde = Sonde(datastream, config.site)
    sonde.run(datastore, timeout=1)
