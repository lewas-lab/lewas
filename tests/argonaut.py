#!/usr/bin/env python2

import sys, re
sys.path.append('../')
import lewas.models
from lewas.parsers import UnitParser, AttrParser, field_rangler
import lewas.datastores
   
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
    (float, 'battery', 'input power', 'V'),
    (float, 'beam', 'vertical sample start', 'm'),
    (float, 'beam', 'vertical sample end', 'm'),
    (float, 'beam', 'noise level 1', 'counts'),
    (float, 'beam', 'noise level 2', 'counts'),
    (float, 'beam', 'noise level 3', 'counts'),
]    
    
profile_fields = lambda cellnum: [
    (float, 'beam', 'cell number', None),
    UnitParser(float, ('water', 'downstream velocity'), 'cm/s', offset=('cell', cellnum) ),
    UnitParser(float, ('water', 'lateral velocity'), 'cm/s', offset=('cell', cellnum) ),
    AttrParser(float, 'stderr', has_attr( 'metric', ('water', 'downstream velocity'), () ) ), # and m.offset == ('cell', cellnum) ),
    AttrParser(float, 'stderr', has_attr( 'metric', ('water', 'lateral velocity'), () ) ), # and m.offset == ('cell', cellnum) ),
    UnitParser(float, ('beam', 'signal strength 1'), 'counts', offset=('cell', cellnum) ),
    UnitParser(float, ('beam', 'signal strength 2'), 'counts', offset=('cell', cellnum) ),
]

class Argonaut(lewas.models.Instrument):
    fields = [ field_rangler(f) for f in argo_fields ]
    parsers = { r'(([0-9\.\-]+ +){30}[0-9\.\-]+)': lewas.parsers.split_parser(delim=' ',fields=fields) }
    for i in range(1, 11):
        fields = [ field_rangler(f) for f in profile_fields(i) ]
        parsers['( *%s +([0-9\.\-]+ +){5}[0-9\.\-]+)' % i] = \
                lewas.parsers.split_parser(delim=' ', fields=fields)
       
if __name__ == '__main__':
    site = 'test1'
    if len(sys.argv) == 1:
        datastream = open("argonaut_data1.txt", "r")
        #datastore = lewas.datastores.IOPrinter()
        datastore = lewas.datastores.leapi('http://localhost:5050')
        site = 'test1'
    else:
        import serial
        datastream = serial.Serial("/dev/tty{}".format(sys.argv[1]), 9600) #argv[1] e.g. USB0
        datastore = lewas.datastores.leapi()
        site = 'stroubles1'
        
    argo = Argonaut(datastream, site)
    argo.run(datastore)

