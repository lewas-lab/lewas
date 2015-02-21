#!/usr/bin/env python2

import sys
sys.path.append('../')

## What is clearer, a class structure

import serial
import re
import lewas.models
import lewas.parsers
import lewas.datastores

if __name__ == '__main__':
    datastream = serial.Serial("/dev/tty{}".format(sys.argv[1]), 9600, xonxoff=0) #argv[1] e.g. USB0
    for line in datastream:
        print("line: {}".format(line))
