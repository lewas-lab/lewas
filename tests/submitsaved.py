#!/usr/bin/env python2

import pickle, sys, os
sys.path.append('../')
from lewas.parsers import UnitParser, AttrParser, field_rangler
import lewas.datastores
import lewas.models

config = "../config"
config = lewas.readConfig(config)
for fn in sys.argv[1:]:
    if not os.path.isfile(fn):
	sys.stderr.write('{}: not a file\n'.format(fn))
        continue
    if lewas.datastores.submitRequest(pickle.load(open(fn)), config, False):
    	base, fn = os.path.split(fn)
    	os.rename(base+os.sep+fn, 'request_complete'+os.sep+fn)
	#print "moving {} to {}".format(base+os.sep+fn, 'request_complete'+os.sep+fn) 
    #print "processed", fn
