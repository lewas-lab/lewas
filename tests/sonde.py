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

decorations = { '#': ('out_of_range','Data out of sensor range'),
                '?': ('service_required','User service required or data outside calibrated range but still within sensor range'),
                '*': ('not_calibrated','Parameter not calibrated'),
                '~': ('temperature_compensation_error','Temperature compensation error'),
                '@': ('compensation_error','Non temperature parameter compensation error'),
              }
    

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

    @property
    def flags(self):
        try:
            return [ decorations[self.qualifier][0] ]
        except KeyError:
            return []

def decorated_float(value):
    try:
        return float(value)
    except ValueError:
        m = dfloat_regex.match(value)
        if m:
            qf = QualifiedFloat(m.group(1), m.group(2))
            return qf
    return None

    
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

sonde_headers = { 'Time': ('time', 'HHMMSS'), 
                  'Temp': ('water','temperature'),
                  'pH': ('water','pH'), 
                  'SpCond': ('water','specific conductance'), 
                  'Sal': ('water','salinity'), 
                  'ORP': ('water','Redox potential'), 
                  'TurbSC': ('water','turbidity'), 
                  'LDO%': ('water', 'LDO%'),
                  'LDO': ('water', 'dissolved oxygen'),
                  'Dep100': ('water', 'depth'),
                  'IBatt': ('battery', 'voltage'),
                  'EBatt': ('battery', 'voltage')
}

sonde_typef = { 'Time': str }

sonde_units = { '\xf8C': 'C',
		'Sat': '%',
		'Units': 'pH',
        'meters', 'm'
        'HHMMSS': None
   }

def typef_from_header(label):
    try:
        return sonde_typef[label]
    except KeyError:
        return decorated_float

def units_from_header(label):
    try:
        return sonde_units[label]
    except KeyError:
        return label

def parser_from_header(label, units):
    return lewas.parsers.UnitParser(decorated_float,sonde_headers[label],units_from_header(units))

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
            if lineno > 4:
                break
            headers.append(line.strip().split())

	logging.debug(('headers: {}\n'.format(headers[3:4])))
        (metrics, units) = headers[3:5]
        fields = [ parser_from_header(mn,u) for (mn,u) in zip(metrics,units) ]
        return fields
    
    def init(self):
        try:
            self.datastream.write('   ')
        except IOError:
            self.fields = [ lewas.parsers.UnitParser(t,(mm,mn),u) for t,mm,mn,u in sonde_fields ]
        else:
            self.fields = self._fields_from_stream()
            logging.debug('fields: {}'.format(self.fields))
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
        timeout=3
        datastream = serial.Serial("/dev/{}".format(sys.argv[1]), 19200, xonxoff=0,timeout=timeout) #argv[1] e.g. USB0
        config = '../config'

    config = lewas.readConfig(config)
    datastore = lewas.datastores.leapi(config)
        
    sonde = Sonde(datastream, config.site)
    sonde.init()
    sonde.run(datastore, timeout=1)
