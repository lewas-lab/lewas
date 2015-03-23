#!/usr/bin/env python2

import pickle, sys
sys.path.append('../')
from lewas.parsers import UnitParser, AttrParser, field_rangler
import lewas.datastores
import lewas.models

config = "../config"
config = lewas.readConfig(config)
lewas.datastores.submitRequest(pickle.load(open(sys.argv[1])), config, False)
