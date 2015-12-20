import logging

#class InstrumentMeta(type):
#       def __new__(cls, name, bases, attrs):
#               attrs['_name'] = attrs.get('__name__', name.lower())
#               return super(InstrumentMeta, cls).__new__(cls, name, bases, attrs)
#
#       def __init__(self, name, bases, attrs):
#               super(InstrumentMeta, self).__init__(name, bases, attrs)

logger = logging.getLogger(__name__)

class Instrument(object):
    """
    class representing an instrument
    """

    #__metaclass__ = InstrumentMeta

    def __init__(self, datastream, site="test1", **kwargs):
        self.name = kwargs.get('name', getattr(self, '__name__', self.__class__.__name__.lower()))
        self.datastream = datastream
        self.site = site
        self.parsers = kwargs.get('parser', getattr(self, 'parsers', None))
        #for (prop,value) in inspect.getmembers(self):
        #    print("{0}: {1}".format(prop,value))

        #for (prop,value) in vars(self).iteritems():
        #    print("{0}: {1}".format(prop,value))

    def _populat_measurement(self, m):
        setattr(m, 'instrument', self.name)
        setattr(m, 'station', self.site)
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
