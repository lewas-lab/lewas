import re

class Measurement:
    def __init__(self, value, metric, unit, instrument="", station=""):
        self.value = value
        self.metric = metric
        self.unit = unit
        self.instrument = instrument
        self.station = station

    def __repr__(self):
        return "{}/{}/{}: {} {}".format(self.station, self.instrument, self.metric, self.value, self.unit)

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

    def __init__(self, datastream, site="test1"):
        self.name = self.__class__.__name__
        self.datastream = datastream
        self.site = site
        #for (prop,value) in inspect.getmembers(self):
        #    print("{0}: {1}".format(prop,value))
            
        #for (prop,value) in vars(self).iteritems():
        #    print("{0}: {1}".format(prop,value))

    def __repr__(self):
        return "Instrument: {0}".format(self.name)

    def run(self, datastore, **kwargs):
        for line in self.datastream:
            try:
                measurements = [ m for m in self.parse(line) if m ]
            except ValueError as e:
                print("ParseError: {}\ndata: {}".format(str(e), line))
            else:
                datastore.post(measurements, **kwargs)

    def parse(self, line):
        # go through list of user supplied parsers, find a line that matches
        result = []
        if hasattr(self.parsers, 'items'):
            for (pat, parser) in self.parsers.items():
                pat = re.compile(pat)
                m = pat.match(line)
                if m:
                    result = parser(m.group(1))
        else:
            result = getattr(self,'parsers')(line)
            
        return result
                

if __name__ == '__main__':
    import sys

    class MyInstrument(Instrument):
        pass
    
    myinstrument = MyInstrument(sys.stdout)

    print(myinstrument)
