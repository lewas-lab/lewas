import re
import logging
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

TZ = pytz.timezone('US/Eastern') # TODO: move to config parameter

class Measurement:
    def __init__(self, value, metric, unit, **kwargs):
        logger.log(logging.DEBUG, 'value: {}, kwargs: {}'.format(value, kwargs))
        self.value = value
        self.metric = metric
        self.unit = unit
        self.stderr = kwargs.get('stderr', None)
        self.instrument = kwargs.get('instrument', "")
        self.station = kwargs.get('station', "")
        self.offset = kwargs.get('offset', ())
        self.datetime = kwargs.get('datetime', datetime.now(TZ))
        self.flags = kwargs.get('flags', None)
        
    def __getitem__(self, name):
        return getattr(self, name)

    def __repr__(self):
        _repr = "{}/{}/{}: {} {}".format(self.station, self.instrument, self.metric, self.value, self.unit)
        _options = { option: getattr(self, option)  for option in ['stderr', 'offset', 'flags'] \
                if getattr(self, option, None) is not None }

        if _options:
            _repr = _repr + ' {}'.format(_options)
        return _repr

    def __nonzero__(self):
        return self.value is not None and self.metric is not None and self.unit is not None
 
