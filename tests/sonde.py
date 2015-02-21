#!/usr/bin/env python2

import sys
sys.path.append('../')

## What is clearer, a class structure

import re
import lewas.models
import lewas.parsers
import lewas.datastores

weather_station_metrics = { 'Pa': ( 'air', 'pressure', 'hPa' ),
                            'Rc': ( 'rain', 'accumulation', 'mm' ),
                            'Rd': ( 'rain', 'duration', 's' ),
                            'Ri': ( 'rain', 'intensity', 'mm/h' ),
                            'Ta': ('air', 'temperature', 'F'),
                            'Hc': ( 'hail', 'accumulation', 'hits/cm2' ),
                            'Hd': ( 'hail', 'duration', 's' ),
                            'Hi': ( 'hail', 'intensity', 'hits/cm2h'),
                            'Sm': ('wind', 'speed', 'm/s'),
                            'Vs': ('battery', 'voltage', 'V'),
                            'Dm': ('wind', 'direction', 'D'),
                            'Ua': ('air', 'humidity', '%RH')
}

unit_conversion = { 'H': 'hPa',
                    'P': '%RH',
                    'M': 'mm',
                    
                }

def sonde_helper(astring):
    """A helper should take a string representing a single measurement and
    return a tuple or object representing that value. In this case we
    return a Measurement object, the parser will then return a list of
    Measurement objects
    """

    (key, value) = astring.split("=")
    units = None
    if key in weather_station_metrics:
        key = weather_station_metrics[key]
        units = key[2]
    m = None    
    try:
        (value,unit) = re.search(r'([0-9]+(?:\.[0-9]+)?)([a-zA-Z#/]+)',value).groups()
        m = lewas.models.Measurement(value, key, units, "weather station", "stroubles1")
    except AttributeError, e:
        print("Error parsing: {}".format(value))
    return m

class unitParser():
    def __init__(self,typef,metric,units,instrument,site):
        self.typef = typef
        self.metric = metric 
        self.units = units
        self.instrument = instrument
        self.site = site

    @property
    def units(self):
        return self.units

    @property
    def metric(self):
        return self.metrics
    
    def __call__(self,value):
        v = self.typef(value)
        return lewas.models.Measurement(value,self.metric,self.units,self.instrument,self.site)

    def __repr__(self):
        return "unitParser ({})".format((self.typef,self.metric,self.units,self.instrument,self.site))
    
class timeParser(unitParser):
    pass

sonde_fields = [ (str, 'time', 'HHMMSS', 'time'),
               (float, 'water', 'temperature','C'),
               (float, 'water', 'pH','pH'),
               (float, 'water', 'specific conductance', 'mS/cm'),
               (float, 'water', 'depth', 'm'),
               (float, 'water', 'LDO%', '%'),
               (float, 'water', 'dissolved oxygen', 'mg/l'),
               (float, 'water', 'turbidity', 'NTU'),
               (float, 'water', 'Redox potential', 'mV'),
               (float, 'battery', 'voltage', 'V')
               ]

class Sonde(lewas.models.Instrument):
    fields = [ unitParser(t,(mm,mn),u,"sonde","stroubles1") for t,mm,mn,u in sonde_fields ]
        
    parsers = { r'(.*)': lewas.parsers.split_parser(delim=' ',fields=fields) }

    def start(self):
        pass
        
if __name__ == '__main__':
    if len(sys.argv) == 1:
        datastream = open("sonde_data.txt", "r")
    else:
        import serial
        datastream = serial.Serial("/dev/tty{}".format(sys.argv[1]), 19200, xonxoff=0) #argv[1] e.g. USB0

    sonde = Sonde(datastream)
    sonde.run(lewas.datastores.leapi())
