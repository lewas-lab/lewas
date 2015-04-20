import re
import logging
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

TZ = pytz.timezone('US/Eastern') # TODO: move to config parameter

class Measurement:
    def __init__(self, value, metric, unit, **kwargs):
        self.value = value
        self.metric = metric
        self.unit = unit
        self.stderr = kwargs['stderr'] if 'stderr' in kwargs else None
        self.instrument = kwargs['instrument'] if 'instrument' in kwargs else ""
        self.station = kwargs['station'] if 'station' in kwargs else ""
        self.offset = kwargs['offset'] if 'offset' in kwargs else ()
        self.time = str(datetime.now(TZ))

    def __repr__(self):
        return "{}/{}/{}: {} {} (stderr: {}, offset: {})".format(self.station, self.instrument, self.metric, self.value, self.unit, self.stderr, self.offset)

    def __iter__(self):
        return ((a, getattr(self, a)) for a in ["metric", "value", "unit", "instrument", "station"])

    def __nonzero__(self):
        return self.value is not None and self.metric is not None and self.unit is not None
    
class Sensor:
    def __init__(self, **kwargs):
        [ setattr(self, key, value) for key,value in kwargs.items() if key in ['metric','unit','type'] ]

#class ModelBase(type):
#    def __init__(cls, name, bases, nmspc):
#        super(ModelBase, cls).__init__(name, bases, nmspc)
#        cls.name = name
#
#        print([m for m in dir(cls) if not m.startswith('__')])


class Instrument(object):
    """
    class representing an instrument
    """
    #def __new__(cls, *args, **kwargs):
    #    try:
    #        inst = object.__new__(cls)
    #    except TypeError:
    #        pass
    #    else:
    #        return inst

    def __init__(self, datastream, site="test1", **kwargs):
        self.name = self.__class__.__name__ if 'name' not in kwargs else kwargs['name']
        self.datastream = datastream
        self.site = site
        #for (prop,value) in inspect.getmembers(self):
        #    print("{0}: {1}".format(prop,value))
            
        #for (prop,value) in vars(self).iteritems():
        #    print("{0}: {1}".format(prop,value))

    def _populat_measurement(self,m):
        setattr(m,'instrument', self.name.lower())
        setattr(m,'station', self.site)
        return m
    
    def __repr__(self):
        return "Instrument: {0}".format(self.name)

    def run(self, datastore, **kwargs):
        if 'site_id' not in kwargs:
            kwargs['site_id'] = self.site
        
        timeout = kwargs.get('timeout', 0)

        if timeout:
            if not hasattr(self.datastream, 'timeout'):
                logging.warn("datastream {} does not have a timeout attribute, is it a PySerial stream?\n".format(self.datastream))
            while True:
                try:
                    self._readlines(datastore, **kwargs)
                except (KeyboardInterrupt, SystemExit):
                    break
        else:
            self._readlines(datastore, **kwargs)

    def parse(self, line):
        # go through list of user supplied parsers, find a line that matches
        result = []
	logger.log(logging.INFO,"line:{}".format(line))
        if hasattr(self.parsers, 'items'):
            for (pat, parser) in self.parsers.items():
                pat = re.compile(pat)
                m = pat.match(line)
                if m:
                    result = parser(m.group(1))
        else:
            result = getattr(self,'parsers')(line)
            
        return result
                
    def _readlines(self, datastore, **kwargs):
        measurements = []
        timeout = kwargs.get('timeout', 0)
        for line in self.datastream:
            try:
                measurements = measurements + [ self._populat_measurement(m) for m in self.parse(line) if m ]
            except ValueError as e:
                print("ParseError: {}\ndata: {}".format(str(e), line))
            else:
                if not timeout:
                    datastore.post(measurements, **kwargs)
                    measurements = []
        if timeout:
            datastore.post(measurements, **kwargs)

if __name__ == '__main__':
    import sys

    class MyInstrument(Instrument):
        pass
    
    myinstrument = MyInstrument(sys.stdout)

    print(myinstrument)
