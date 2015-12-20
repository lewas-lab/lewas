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
        self.stderr = kwargs.get('stderr', None)
        self.instrument = kwargs.get('instrument', "")
        self.station = kwargs.get('station', "")
        self.offset = kwargs.get('offset', ())
        self.datetime = datetime.now(TZ)
        self.flags = kwargs.get('flags', [])
        
    def __getitem__(self, name):
        return getattr(self, name)

    def __repr__(self):
        return "{}/{}/{}: {} {} (stderr: {}, offset: {})".format(self.station, self.instrument, self.metric, self.value, self.unit, self.stderr, self.offset)

    def __iter__(self):
        return ((a, getattr(self, a)) for a in ["metric", "value", "unit", "instrument", "station"])

    def __nonzero__(self):
        return self.value is not None and self.metric is not None and self.unit is not None
 
