#!/usr/bin/env python2

import logging
import os
import re
import sys
sys.path.append('../')

from lewas.parsers import UnitParser, AttrParser, field_rangler
import lewas.datastores
import lewas.models
   
#see page 257 of manual
#2015 02 22 09 43 51     7.4     0.4   0.376   4.1   4.0  10.0 194 191 139   0    0.0   0.0   0.0  0.0  0.0  0.0   4.06      0.000    0.000  11.6   0.1    0.4  30  30  29

def has_attr(attr, value, default=None):
    return lambda m: getattr(m, attr, default) == value

argo_fields = [
    UnitParser(int, ('time','hour'), None),
    UnitParser(int, ('time', 'month'), None),
    UnitParser(int, ('time', 'day'), None),
    UnitParser(int, ('time', 'hour'), None),
    UnitParser(int, ('time', 'minute'), None),
    UnitParser(int, ('time', 'second'), None),
    UnitParser(float, ('water', 'downstream velocity'), 'cm/s'),
    UnitParser(float, ('water', 'lateral velocity'), 'cm/s'),
    UnitParser(float, ('water', 'depth'), 'm'),
    AttrParser(float, 'stderr', has_attr( 'metric', ('water', 'downstream velocity'), () ) ),
    AttrParser(float, 'stderr', has_attr( 'metric', ('water', 'lateral velocity'), () ) ),
    AttrParser(float, 'stderr', has_attr( 'metric', ('water', 'depth'), () ) ),
    UnitParser(float, ('beam', 'signal strength 1'), 'counts'),
    (float, 'beam', 'signal strength 2', 'counts'),
    (float, 'beam', 'signal strength 3', 'counts'),
    (float, 'pings', 'good', None),
    (float, 'package', 'heading', None),
    (float, 'package', 'pitch', None),
    (float, 'package', 'roll', None),
    (float, 'package', 'heading stdev', None),
    (float, 'package', 'pitch stdev', None),
    (float, 'package', 'roll stdev', None),
    (float, 'water', 'temperature', 'C'),
    (float, 'water', 'pressure', None),
    AttrParser(float, 'stderr', lambda x: x.metric == ('water', 'pressure')),
    (float, 'battery', 'voltage', 'V'),
    (float, 'beam', 'vertical sample start', 'm'),
    (float, 'beam', 'vertical sample end', 'm'),
    (float, 'beam', 'noise level 1', 'counts'),
    (float, 'beam', 'noise level 2', 'counts'),
    (float, 'beam', 'noise level 3', 'counts'),
]    
    
def profile_fields(cellnum):
    return [
        (float, 'beam', 'cell number', None),
        UnitParser(float, ('water', 'downstream velocity'), 'cm/s', offset=('cell', cellnum) ),
        UnitParser(float, ('water', 'lateral velocity'), 'cm/s', offset=('cell', cellnum) ),
        AttrParser(float, 'stderr', has_attr( 'metric', ('water', 'downstream velocity'), () ) ), # and m.offset == ('cell', cellnum) ),
        AttrParser(float, 'stderr', has_attr( 'metric', ('water', 'lateral velocity'), () ) ), # and m.offset == ('cell', cellnum) ),
        UnitParser(float, ('beam', 'signal strength 1'), 'counts', offset=('cell', cellnum) ),
        UnitParser(float, ('beam', 'signal strength 2'), 'counts', offset=('cell', cellnum) ),
    ]

start_line = r'(([0-9\.\-]+ +){30}[0-9\.\-]+)'
start_re = re.compile(start_line)
cell_state_re = re.compile(r'cell[1-10]')

    
class Argonaut(lewas.models.Instrument):
    fields = [ field_rangler(f) for f in argo_fields ]
    parsers = { r'(([0-9\.\-]+ +){30}[0-9\.\-]+)': lewas.parsers.split_parser(delim=' ',fields=fields) }
    for i in range(1, 11):
        fields = [ field_rangler(f) for f in profile_fields(i) ]
        parsers['( *%s +([0-9\.\-]+ +){5}[0-9\.\-]+)' % i] = \
                lewas.parsers.split_parser(delim=' ', fields=fields)
       
if __name__ == '__main__':
    logging.basicConfig(level=getattr(logging, os.environ.get('LOGGING_LEVEL','WARN')))
    timeout = 0
    if len(sys.argv) == 1:
        datastream = open("argonaut_data_209.txt", "r")
        config = '../config.example'
    else:
        import serial
        timeout=1
        datastream = serial.Serial("/dev/{}".format(sys.argv[1]), 9600, timeout=timeout) #argv[1] e.g. USB0
        config = "../config"

    config = lewas.readConfig(config)
    datastore = lewas.datastores.leapi(config)
        
    argo = Argonaut(datastream, config.site)
    argo.run(datastore, timeout=timeout)

