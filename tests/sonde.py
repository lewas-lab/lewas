#!/usr/bin/env python2

import logging
import os
import re
import sys
sys.path.append('../')

## What is clearer, a class structure

import lewas.models
import lewas.parsers 
import lewas.datastores

# NOTE: fields and field order are determined by the configuration of
# the Sonde and are not necessarily constant. Eventually we should add
# a getHeaders() function that retreives and parses the column header
# from the Sonde. To do that, send three space characters, wait for
# H?:, send 'H', read two lines, those should be the headers

dfloat_regex = re.compile(r'([0-9]+(?:\.[0-9]+)?)([*~@#?])')

class QualifiedFloat():
    def __init__(self, value, qualifier):
        self.value = value
        self.qualifier = qualifier

    def __float__(self):
        return self.value

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)
    
def decorated_float(value):
    try:
        return float(value)
    except ValueError:
        m = dfloat_regex.match(value)
        if m:
            qf = QualifiedFloat(m.group(1), m.group(2))
            return qf
    return None

decorations = { '#': 'Data out of sensor range',
                '?': 'User service required or data outside calibrated range but still within sensor range',
                '*': 'Parameter not calibrated',
                '~': 'Temperature compensation error',
                '@': 'Non temperature parameter compensation error'
                }
    
    
sonde_fields = [ (str, 'time', 'HHMMSS', None),
               (decorated_float, 'water', 'temperature','C'),
               (decorated_float, 'water', 'pH','pH'),
               (decorated_float, 'water', 'specific conductance', 'mS/cm'),
               (decorated_float, 'water', 'salinity', 'ppt'),  
               (decorated_float, 'water', 'Redox potential', 'mV'),
               (decorated_float, 'water', 'turbidity', 'NTU'),
               (decorated_float, 'water', 'LDO%', '%'),
               (decorated_float, 'water', 'dissolved oxygen', 'mg/l')
               ]

class Sonde(lewas.models.Instrument):
            
    def start(self):
        pass

    def _fields_from_stream(self):
        for line in self.datastream:
            if line.startswith('HM?:'):
                break

        self.datastream.write('H\r\n')

        headers = []
        for (lineno, line) in enumerate(self.datastream):
            if lineno > 3:
                break
            headers.append(line.split())

        (metrics, units) = headers[3:4]
        fields = [ lewas.parsers.UnitParser(decorated_float,'water',mn,u) for (mn,u) in zip(metrics,units) ]
        return fields
    
    def init(self):
        try:
            self.datastream.write('   ')
        except IOError:
            self.fields = [ lewas.parsers.UnitParser(t,(mm,mn),u) for t,mm,mn,u in sonde_fields ]
        else:
            self.fields = self._fields_from_stream()
        finally:
            #fields = [ lewas.parsers.UnitParser(t,(mm,mn),u) for t,mm,mn,u in sonde_fields ]
            self.parsers = { r'(.*)': lewas.parsers.split_parser(delim=' ',fields=self.fields) }


if __name__ == '__main__':
    logging.basicConfig(level=getattr(logging, os.environ.get('LOGGING_LEVEL','WARN')))
    timeout=0
    if len(sys.argv) == 1:
        datastream = open("sonde_data.txt", "r")
        config = '../config.example'
    else:
        import serial
        timeout=1
        datastream = serial.Serial("/dev/{}".format(sys.argv[1]), 19200, xonxoff=0,timeout=timeout) #argv[1] e.g. USB0
        config = '../config'

    config = lewas.readConfig(config)
    datastore = lewas.datastores.leapi(config)
        
    sonde = Sonde(datastream, config.site)
    sonde.init()
    sonde.run(datastore, timeout=1)
