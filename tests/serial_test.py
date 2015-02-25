#!/usr/bin/env python2

import sys
sys.path.append('../')

## What is clearer, a class structure

import re
import argparse

if __name__ == '__main__':
    print(sys.argv)
    baud = sys.argv[2]
    args = {}
    if len(sys.argv) > 2:
        args = dict( [ (lambda p: p.split('='))(x) for x in sys.argv[2:]])

    import serial
    #datastream = serial.Serial("/dev/tty{}".format(sys.argv[1]), baud, **args) #argv[1] e.g. USB0
    datastream = serial.Serial("/dev/tty{}".format(sys.argv[1]), baud, stopbits=serial.STOPBITS_ONE) #argv[1] e.g. USB0
    
    for line in datastream:
        sys.stdout.write(line)
