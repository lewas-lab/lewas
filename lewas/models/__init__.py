from collections import namedtuple

from measurement import Measurement
from instrument import Instrument

Metric = namedtuple('Metric', ['medium', 'name'])
Unit = namedtuple('Unit', ['abbv'])
Offset = namedtuple('Offset', ['type', 'value'])

__all__ = [ 'measurement', 'instrument' ]
