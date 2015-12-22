from splitparser import split_parser
from unitparser import UnitParser
from attrparser import AttrParser

__all__ = [ 'split_parser', 'UnitParser', 'AttrParser', 'ParseError' ]

class Field():
    def __init__(self, typef, metric, unit):
        self.type = typef
        self.metric = metric
        self.unit = unit

class ParseError(RuntimeError):
    pass

# helper function to ease transition of legacy field lists
def field_rangler(thing):
    res = UnitParser(thing[0], thing[1:3], thing[3]) if isinstance(thing,tuple) else thing
    return res
