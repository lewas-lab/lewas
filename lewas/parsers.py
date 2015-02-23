import re
import models

__all__ = [ 'split_parser', 'ParseError' ]

class ParseError(RuntimeError):
    pass

def split_parser(**kwargs):
    return lambda astring: _split_parser(astring, **kwargs)

def _split_parser(astring, **kwargs):
    """regexp: a regular expression that will be applied to the full line, 
               string to parse should be in the first match group
       astring: the string to parse
       delim:   character to split string on
    """
    delim = " "
    if 'delim' in kwargs:
        delim = kwargs['delim']

    if 'regexp' in kwargs:
        try:
            values = kwargs['regexp'].search(astring).group(1).split(delim)
        except AttributeError as e:
            raise ParseError("/{0}/ does not match '{1}'".format(kwargs['regexp'].pattern,astring))
    else:
        values = filter(None,astring.split(delim))

    if 'types' in kwargs:
        types = kwargs['types']
    else:
        types = [float]*len(values)
        
    if 'helper' in kwargs:
        return [ kwargs['helper'](value) for value in values ]
    elif 'fields' in kwargs:
        fields = kwargs['fields']
        return [ p(v) for p,v in zip(fields,values) ]
    else:
        return [ typef(value) for (typef,value) in zip(types,values) ]

class unitParser():
    def __init__(self,typef,metric,units,**kwargs):
        self.typef = typef
        self.metric = metric
        self.units = units
        self.instrument = kwargs['instrument'] if 'instrument' in kwargs else None
        #self.sensor = kwargs['sensor']
        self.site = kwargs['site'] if 'site' in kwargs else None

    @property
    def units(self):
        return self.units

    @property
    def metric(self):
        return self.metrics

    def __call__(self,value):
        v = self.typef(value)
        return models.Measurement(value,self.metric,self.units,self.instrument,self.site)

    def __repr__(self):
        return "unitParser ({})".format((self.typef,self.metric,self.units,self.instrument,self.site))
