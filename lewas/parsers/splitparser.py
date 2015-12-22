from unitparser import UnitParser

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
        measurements = [ p(v) for p,v in zip(fields,values) if isinstance(p,UnitParser) ]
        for p,v in zip(fields,values):
            if isinstance(p,AttrParser):
                p(measurements,v)
        #print("measuring: {}".format( [ m.metric for m in measurements ] ))
        return measurements
    else:
        return [ typef(value) for (typef,value) in zip(types,values) ]


