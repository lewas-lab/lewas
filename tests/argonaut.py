#!/usr/bin/env python2

import sys, re
sys.path.append('../')
import lewas.models
import lewas.parsers
import lewas.datastores
   
#see page 257 of manual
#2015 02 22 09 43 51     7.4     0.4   0.376   4.1   4.0  10.0 194 191 139   0    0.0   0.0   0.0  0.0  0.0  0.0   4.06      0.000    0.000  11.6   0.1    0.4  30  30  29
argo_fields = [
    (int, 'time', 'year', None),
    (int, 'time', 'month', None),
    (int, 'time', 'day', None),
    (int, 'time', 'hour', None),
    (int, 'time', 'minute', None),
    (int, 'time', 'second', None),
    (float, 'water', 'downstream velocity', 'cm/s'),
    (float, 'water', 'lateral velocity', 'cm/s'),
    (float, 'water', 'depth', 'm'),
    (float, 'water', 'downstream velocity std error', 'cm/s'),
    (float, 'water', 'lateral velocity std error', 'cm/s'),
    (float, 'water', 'depth std error', 'm'),
    (float, 'beam', 'signal strength 1', 'counts'),
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
    (float, 'water', 'pressure stdev', None),
    (float, 'battery', 'input power', 'V'),
    (float, 'beam', 'vertical sample start', 'm'),
    (float, 'beam', 'vertical sample end', 'm'),
    (float, 'beam', 'noise level 1', 'counts'),
    (float, 'beam', 'noise level 2', 'counts'),
    (float, 'beam', 'noise level 3', 'counts'),
]

class Argonaut(lewas.models.Instrument):
    fields = [ lewas.parsers.unitParser(t,(mm,mn),u) for t,mm,mn,u in argo_fields ]
    parsers = { r'(.{80}.*)': lewas.parsers.split_parser(delim=' ',fields=fields) }
       
if __name__ == '__main__':
    site = 'test1'
    if len(sys.argv) == 1:
        datastream = open("argonaut_data_one_stopbit.txt", "r")
    else:
        import serial
        datastream = serial.Serial("/dev/tty{}".format(sys.argv[1]), 9600) #argv[1] e.g. USB0
        site = 'stroubles1'
        
    argo = Argonaut(datastream, site)
    argo.run(lewas.datastores.leapi())

