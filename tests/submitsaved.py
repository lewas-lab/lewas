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
        print "can't read " + fn
        continue
    lewas.datastores.submitRequest(pickle.load(open(fn)), config, False)
    print "processed", fn
