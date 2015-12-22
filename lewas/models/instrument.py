import logging
from itertools import izip, cycle

#class InstrumentMeta(type):
#       def __new__(cls, name, bases, attrs):
#               attrs['_name'] = attrs.get('__name__', name.lower())
#               return super(InstrumentMeta, cls).__new__(cls, name, bases, attrs)
#
#       def __init__(self, name, bases, attrs):
#               super(InstrumentMeta, self).__init__(name, bases, attrs)

logger = logging.getLogger(__name__)

def tokenParser(stream, parsers, **kwargs):
    """take a stream of tokens and a list of parsers, return an iterator over measurements"""
    timeout = kwargs.get('timeout', None)
    for token, parser in izip(stream, cycle(parsers)):
        m = parser(token)
        logging.info('created measurement {}'.format(m))
        if not timeout:
            yield [m]

class Instrument(object):
    """
    class representing an instrument
    """

    #__metaclass__ = InstrumentMeta

    def __init__(self, datastream, site="test1", **kwargs):
        self.name = kwargs.get('name', getattr(self, '__name__', self.__class__.__name__.lower()))
        self.datastream = datastream
        if hasattr(self, 'init'):
            self.init()
        self.site = site
        self.parsers = kwargs.get('parser', getattr(self, 'parsers', None))

    def _populate_measurement(self, m):
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

    def _readlines(self, datastore, **kwargs):
        tokenizer=kwargs.pop('tokenizer', None)
        datastream = self.datastream if tokenizer is None else tokenizer(self.datastream)
        logging.info('reading from datastream {}'.format(datastream))
        for measurements in tokenParser(datastream, self.parsers, **kwargs):
            logging.info('posting {} measurements as 1 request'.format(len(measurements)))
            datastore.post([ self._populate_measurement(m) for m in measurements if m.unit is not None ], **kwargs)
