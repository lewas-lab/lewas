#!/usr/bin/env python2

import logging
import os
import re
import sys
sys.path.append('../')

import lewas.models
import lewas.parsers
import lewas.datastores

weather_station_metrics = { 'Pa': ( 'air', 'pressure', {'H': 'hPa', 'I': 'inHg', 'P': 'Pascal', 'B': 'Bar', 'M': 'mmHg'} ),
                            'Rc': ( 'rain', 'accumulation', {'M': 'mm', 'I': 'in'} ),
                            'Rd': ( 'rain', 'duration', 's' ),
                            'Ri': ( 'rain', 'intensity', {'M': 'mm/h', 'I': 'in/h'} ),
                            'Ta': ('air', 'temperature', {'F': 'F', 'C': 'C'}),
                            'Hc': ( 'hail', 'accumulation', {'M': 'hits/cm2', 'I': 'hits/in2'} ),
                            'Hd': ( 'hail', 'duration', 's' ),
                            'Hi': ( 'hail', 'intensity', {'M': 'hits/cm2h', 'I': 'hits/in2h'}),
                            'Sm': ('wind', 'speed', 'm/s'),
                            'Vs': ('battery', 'voltage', 'V'),
                            'Dm': ('wind', 'direction', 'degrees'),
                            'Ua': ('air', 'humidity', '%RH')
}

def weather_helper(astring):
    """A helper should take a string representing a single measurement and
    return a tuple or object representing that value. In this case we
    return a Measurement object, the parser will then return a list of
    Measurement objects
    """

    (key, value) = astring.split("=")
    kkey = key
    units = None
    if key in weather_station_metrics:
        key = weather_station_metrics[key]
        units = key[2]
    m = None    
    try:
        (value,unit) = re.search(r'([0-9]+(?:\.[0-9]+)?)([a-zA-Z#/]+)',value).groups()
        if unit == '#':
            sys.stderr.write("Invalid data: {}={}\n".format(kkey,value))
        else:
            if hasattr(units,'get'):
                units = units.get(unit, None)
            m = lewas.models.Measurement(value, key[0:2], units)
    except AttributeError, e:
        sys.stderr.write("Error parsing: {}\n".format(value))
    return m

class WeatherStation(lewas.models.Instrument):
    ## should we define sensors in an array
    sensors = { 'wind.DirectionMin': { 'metric': 'wind_speed', 'unit': 'm/s' },
                'wind.DirectionAvg': { 'metric': 'wind_speed', 'unit': 'm/s' },
                'wind.DirectionMax': { 'metric': 'wind_speed', 'unit': 'm/s' }
            }

    ## let's just use the output of the sensor to determine metrics: one parser to rule them all.
    parsers = { r'^0R[0-5],(.*)': lewas.parsers.split_parser(delim=',',helper=weather_helper) }

    def __init__(self,datastream,site):
        super(WeatherStation,self).__init__(datastream,site,name='weather_station')
        
    ## still figuring out what makes sense here
    #DirectionMin = lewas.models.Sensor(metric='wind_speed', unit='m/s')
    #WindGust = lewas.models.Sensor(metric='wind_gust', unit='m/s')


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
    logging.basicConfig(level=getattr(logging, os.environ.get('LOGGING_LEVEL','WARN')))
    timeout=0
    if len(sys.argv) == 1:
        datastream = open("weather_data.txt", "r")
        config = '../config.example'
    else:
        import serial
        timeout=1
        datastream = serial.Serial("/dev/{}".format(sys.argv[1]), 19200, timeout=timeout) #argv[1] e.g. ttyUSB0
        config = "../config"

    config = lewas.readConfig(config)
    datastore = lewas.datastores.leapi(config)
        
    ws = WeatherStation(datastream, config.site)
    ws.run(datastore, timeout=timeout)

