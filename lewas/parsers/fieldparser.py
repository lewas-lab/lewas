import logging

logger = logging.getLogger(__name__)

from ..models import Measurement
from ..util import is_indexable_but_not_string

def get_value(key, data):
    if isinstance(key, int):
        return _get_value_for_key(key) 
    elif callable(key):
        return key(data)
    else:
        return key
        # raise NotImplementedError('{}: is not callable or an integer')

def _get_value_for_key(key, obj):
    if is_indexable_but_not_string(obj):
        try:
            return ob[key]
        except (IndexError, TypeError, KeyError):
            pass # probably raise a ParseError on (IndexError, TypeError, KeyError)
    return gettattr(obj, key)

def to_marshable_type(field, obj):
    d =  { k: get_value(field[idx], obj) for idx,k in enumerate(['value', 'metric', 'unit']) }
    try:
        d.update(d['value'].__dict__)
    except AttributeError:
        pass
    return d

def to_measurement(obj):
    logger.log(logging.DEBUG, 'creating measurement from {}'.format(obj))
    value = obj.pop('value')
    metric = obj.pop('metric')
    unit = obj.pop('unit')
    return Measurement(value, metric, unit, **obj)

def field_parser(fields, **kwargs):
    def inner(data):
        # todo in vebose/debug mode, is there a way to get the highest index asked for in fields and see if it is different than len(data)
        # just spent an hour debugging a problem which was just me passing the wrong fields argument to this 
        # parser (using the fields array for the argonaut header for the cell parser
        to_format = kwargs.get('formatter', to_measurement)
        logger.log(logging.DEBUG, 'parsing with ({}): {}'.format(fields, data))
        objs = [ to_marshable_type(f, data) for f in fields ]
        return [ to_format(obj) for obj in objs ]
    return inner         
