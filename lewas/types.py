import logging
from operator import itemgetter

logger = logging.getLogger(__name__)

class Bunch(object):
    # see http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/?in=user-97991
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class BunchedValue(Bunch):
    def __init__(self, tfunct=float, **kwds):
        super(BunchedValue, self).__init__(**kwds)
        self.tfunct = tfunct

    def __float__(self):
        return self.tfunct(self.value)

    def __int__(self):
        return self.tfunct(self.value)

    def __str__(self):
        return str(self.value)

def bunch_type(**kwargs):
    def inner(value):
        logger.log(logging.DEBUG, 'bunch_type({})({})'.format(kwargs,value))
        klass = kwargs.get('klass', Bunch)
        for attr, fn in kwargs.items():
            if attr != 'klass':
                logger.log(logging.DEBUG, '{}: fn({}) with fn={}'.format(attr, value, fn))
                (attr, fn(value))
        _specs = { attr: fn(value) for attr, fn in kwargs.items() if attr != 'klass' }
        logger.log(logging.DEBUG, 'creating {} with {}'.format(klass.__name__, _specs))
        return klass(**_specs)
    return inner

def getter_or_fn(idx_or_fn):
    if hasattr(idx_or_fn, '__call__'):
        return idx_or_fn
    else:
        return itemgetter(idx_or_fn)

def itemgetter_float(*args, **kwargs):
    specs = {}
    if args:
        specs = { 'value': itemgetter(args[0]) }
    if kwargs:
        specs.update({ attr: getter_or_fn(idx) for attr,idx in kwargs.items()})

    specs['klass'] = BunchedValue
    return bunch_type(**specs)

class QualifiedFloat():
    def __init__(self, value, **kwargs):
        self.value = float(value)
        self.qualifier = kwargs.get('qualifier', None)
        self.decorations = kwargs.get('decorations', None)
        self.stderr = kwargs.pop('stderr', None)

    def __float__(self):
        return self.value

    def __repr__(self):
        return '<QualifiedFloat: {} {}>'.format(str(self.value), str(self.flags))

    def __str__(self):
        return str(self.value)

    @property
    def flags(self):
        try:
            return [ self.decorations[self.qualifier][0] ]
        except (KeyError, TypeError):
            return []

def decorated_float(decorations):
    def inner(value):
        kwargs = { 'qualifier': value[1], 'decorations': decorations }
        return QualifiedFloat(value[0], **kwargs)
    return inner

def stderr_float(value):
    logger.log(logging.DEBUG, 'creating QualifiedFloat with stderr {}'.format(value[1]))
    return QualifiedFloat(value[0], stderr=value[1])
