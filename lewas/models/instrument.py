import logging
from itertools import izip, imap, cycle, tee, repeat, chain
from lewas.util import is_indexable_but_not_string

logger = logging.getLogger(__name__)

import sys

def chunkReader(chunked_stream):
    while chunked_stream.isOpen():
        chunk = []
        for line in chunked_stream:
            chunked.append(line)
        if chunk:
            yield chunk

def matchedTokenParser(stream, parsers, **kwargs):
    logger.log(logging.DEBUG, 'matchedTokenParser')
    for line in stream:
        for regex, parser in parsers.items():
            m = regex.match(line)
            logger.log(logging.DEBUG, 'matching "{}" to {}'.format(line.strip(), regex.pattern))
            if m:
                logger.log(logging.DEBUG, 'parsing "{}" with {}'.format(m.group(1), parser))
                if m.groups():
                    yield parser(m.group(1))
                else:
                    yield parser(line)
import inspect

def cycleParser(stream, parsers, **kwargs):
    if callable(parsers):
        for line in stream:
            yield parsers(line)
    elif is_indexable_but_not_string(parsers):
        for line, parser in zip(stream, cycle(parsers)):
            yield parser(line)
    else:
        raise NotImplementedError('{}: is not callable or an interrable of callables')
def tokenParser(stream, parsers, **kwargs):
    """take a stream of tokens and a list of parsers, return an iterator over measurements"""
    if hasattr(parsers, 'items'):
        return matchedTokenParser(stream, parsers, **kwargs)
    
    logger.log(logging.DEBUG, 'tokenParser with parser cycle')
    return cycleParser(stream, parsers, **kwargs)

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

        datastream = self.datastream
        parser = self.parsers

        if hasattr(datastream, 'timeout') and getattr(datastream, 'timeout') is not None:
            datastream = chunkReader(datastream)
            parser = chunkParser(parser)

        logger.log(logging.INFO, 'reading from datastream {}'.format(datastream))
        for mlist in tokenParser(datastream, parser):
            logger.log(logging.DEBUG,'posting with mlist {}'.format(mlist))
            datastore.post(map(self._populate_measurement, mlist))
