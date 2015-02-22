#!/usr/bin/env python2

import sys
sys.path.append('../')

## What is clearer, a class structure

import re
import lewas.models
import lewas.parsers
import lewas.datastores

# TODO: move this to parser module
class unitParser():
    def __init__(self,typef,metric,units,**kwargs):
        self.typef = typef
        self.metric = metric 
        self.units = units
        self.instrument = kwargs['instrument']
        self.sensor = kwargs['sensor']
        self.site = kwargs['site']

    @property
    def units(self):
        return self.units

    @property
    def metric(self):
        return self.metrics
    
    def __call__(self,value):
        v = self.typef(value)
        return lewas.models.Measurement(value,self.metric,self.units,self.instrument,self.site)

    def __repr__(self):
        return "unitParser ({})".format((self.typef,self.metric,self.units,self.instrument,self.site))
    
class timeParser(unitParser):
    pass

# NOTE: fields and field order are determined by the configuration of
# the Sonde and are not necessarily constant. Eventually we should add
# a getHeaders() function that retreives and parses the column header
# from the Sonde. To do that, send three space characters, wait for
# H?:, send 'H', read two lines, those should be the headers

sonde_fields = [ (str, 'time', 'HHMMSS', 'time'),
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
    def __init__(self,site):
        self.fields = [ unitParser(t,(mm,mn),u,"sonde",site) for t,mm,mn,u in sonde_fields ]
        self.parsers = { r'(.*)': lewas.parsers.split_parser(delim=' ',fields=fields) }

    def start(self):
        pass
        
if __name__ == '__main__':
    site = 'test1'
    if len(sys.argv) == 1:
        datastream = open("sonde_data.txt", "r")
    else:
        import serial
        datastream = serial.Serial("/dev/tty{}".format(sys.argv[1]), 19200, xonxoff=0) #argv[1] e.g. USB0
        site = 'stroubles1'
        
    sonde = Sonde(datastream, site)
    sonde.run(lewas.datastores.leapi())
