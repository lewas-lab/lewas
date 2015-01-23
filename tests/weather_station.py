#!/bin/env python2

import sys
sys.path.append('../')

## What is clearer, a class structure

import serial
import re
import lewas.models
import lewas.parsers
import lewas.datastores

#from lewas.models import *

class WeatherStation(lewas.models.Instrument):
    def weather_helper(astring):
        """A helper should take a string representing a single measurement and
        return a tuple or object representing that value. In this case we
        return a Measurement object, the parser will then return a list of
        Measurement objects

        """
        
        (key, value) = astring.split("=")
        (value,units) = re.search(r'([0-9]+(?:\.[0-9]+)?)([a-zA-Z#]+)',value).groups()
        m = lewas.models.Measurement(value, key, units)
        return m

    ## should we define sensors in an array
    sensors = { 'wind.DirectionMin': { 'metric': 'wind speed', 'units': 'm/s' },
                'wind.DirectionAvg': { 'metric': 'wind speed', 'units': 'm/s' },
                'wind.DirectionMax': { 'metric': 'wind speed', 'units': 'm/s' }
            }
    ## let's just use the output of the sensor to determine metrics: one parser to rule them all.
    parsers = { r'^0R[0-5],(.*)': lewas.parsers.split_parser(delim=',',helper=weather_helper) }

    ## still figuring out what makes sense here
    DirectionMin = lewas.models.Sensor(metric='wind speed', units='m/s')
    WindGust = lewas.models.Sensor(metric='wind gust', units='m/s')


    #parsers = { r'/^0R1 (.*)$/': lewas.parsers.Split([ "wind.DirectionMin", "wind.DirectionAvg", "wind.DirectMax", "wind.speed", "wind.gust", "wind.lull"]),
    #            r'/^0R2 (.*)$/': lewas.parsers.Split([ "pth.Temp", "pth.Humidity", "pth.Pressure" ]),
    #            r'/^0R3 (.*)$/': lewas.parsers.Split([ "rain.rainAcc", "rain.rainDur", "rain.rainIn", "rain.hailAcc", "rain.hailDur", "rain.hailIn", "rain.peakIn", "rain.hailPeakIn" ])
    #}


    def start(self):
        pass
        
    ## Custom methods.  Anything beyond what is handled by the automatic API
    ## Diagnostic methods

    def check(self, metric):
        codes = { 'wind': '0WU',
          'PTH': '0TU',
          'rain': '0RU',
          'self': '0SU'
        }

        self.cmd_output(codes[metric]+'\n\r')
     
    def reset(self, code):
        codes = { 'rain': '0XZRU',
                  'intensity': '0XZRI'
              }
        output = self.cmd_output(codes[code]+'\n\r')
        

if __name__ == "__main__":
    interactive = False
    
    if len(sys.argv) == 1:
        datastream = open("weather_data.txt", "r")
    else:
        datastream = serial.Serial("/dev/tty{}".format(sys.argv[1]), 19200) #argv[1] e.g. USB0

    ws = WeatherStation(datastream)
    print(ws)
    ws.run(lewas.datastores.RESTPOST())

    #if not interactive:
    #    ws.run(lewas.datastores.ActiveRecord(WeatherStation))
    #else:
    #    pass
        ## run checks, prompt user to reset, check a particular value,
        ## etc.

