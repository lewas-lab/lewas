#!/bin/env python3
import sys
sys.path.append('.')
sys.path.append('../')

import re

from lewas.parsers import *
from lewas.models import *

### Discussion: requiring that we pass metrics and units arrays to
### the parser was not a good design: parsing really doesn't
### require that information, it's just the construction of the
### Measurement object that does. I changed the definition of
### parser to just return a list of coerced values

def weather_helper(astring):
    """A helper should take a string representing a single measurement and
    return a tuple or object representing that value. In this case we
    return a Measurement object, the parser will then return a list of
    Measurement objects

    """

    (key, value) = astring.split("=")
    (value,units) = re.search(r'([0-9]+(?:\.[0-9]+)?)([a-zA-Z]+)',value).groups()
    return Measurement(value, key, units)

if __name__ == '__main__':
    import sys

    string1 = "0R5,Th=25.9C,Vh=12.0N,Vs=15.2V\r\n"

    dataregex = re.compile(r'0R[0-5],(.*)')
    measurements = split_parser(dataregex, string1, ",", helper=weather_helper)
    
    for measurement in measurements:
        print(measurement)

    ### Let's say we have a sensor that just has a simple output
    ### format of comma separated numbers. 

    print("\nAnother sensor")

    string2 = "sensor2: 23.1,34.3,56,34"

    ### We do need to provide the parser an array of units to use and
    ### metrics, presumably we get this from the sensor's
    ### documentation (in this sense, the weather station data format
    ### is rather nice, it allows us to programatically extract unit
    ### information without having to refer to the manual)
    units2 = [ "m/s","mg/L","V","C" ]
    metrics2 = [ "wind speed", "dissolved oxygen", "battery voltage", "temperature" ]
    sensor_regex = re.compile(r'sensor2:\s+(.*)$')
    values = split_parser(sensor_regex, string2, ",", units=units2, metrics=metrics2)

    measurements = [ Measurement(value,metric,unit) for (value,metric,unit) in zip(values,metrics2,units2) ] 
    for m in measurements:
        print(m)


    print("\nNow for a parser on a unparsable string")
    ### Example of exception handling

    string3 = "sensor4: hot,cold,warm"
    try:
        values = split_parser(sensor_regex, string3)
    except ParseError as e:
        sys.stderr.write("ParseError: {0}\ncontinuing...\n".format(e))
                
