from splitparser import split_parser
from fieldparser import field_parser

__all__ = [ 'split_parser', 'field_parser', 'ParseError' ]

class ParseError(RuntimeError):
    pass

def map_parser(fn):
    def inner(data):
        result = map(fn, data)
        return result
    return inner

def debug_parser(label, **kwargs):
    def inner(data):
        wrapper = kwargs.get('wrapper', None)
        sdata = data
        if wrapper:
            sdata = wrapper(data)
        logger.log(logging.DEBUG, '{}: {}'.format(label, sdata))
