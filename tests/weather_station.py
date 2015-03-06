#!/usr/bin/env python2

import sys, re
sys.path.append('../')
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
            print("Invalid data: {}={}".format(kkey,value))
        else:
            m = lewas.models.Measurement(value, key[0:2], units)
    except AttributeError, e:
        print("Error parsing: {}".format(value))
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
        super(WeatherStation,self).__init__(datastream,site,name='weather station')
        
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
    if len(sys.argv) == 1:
        datastream = open("weather_data.txt", "r")
        config = '../config.example'
    else:
        import serial
        datastream = serial.Serial("/dev/tty{}".format(sys.argv[1]), 19200) #argv[1] e.g. USB0
        config = "../config"

    config = lewas.readConfig(config)
    datastore = lewas.datastores.leapi(config)
        
    ws = WeatherStation(datastream, config.site)
    ws.run(datastore)

