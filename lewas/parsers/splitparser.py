import logging
import re

logger = logging.getLogger(__name__)

def split_parser(*args, **kwargs):
    """A split parser accepts a string and splits it on a regular
    expression. If the regular expression contains matching groups,
    those groups are included as items in the output list. See re.split
    for details.
    Optional keyword arguments:
        
        compact: default True, filter any non-Truthy items from result
        """
    def inner(astring):
        try:
            regex = re.compile(args[0])
        except IndexError:
            regex = re.compile(r'\s+')
        logger.log(logging.DEBUG, 'parsing with ({}): {}'.format(regex.pattern, astring))
        result = regex.split(astring)
        if kwargs.get('compact', True):
            result = filter(lambda m: m, result)
        logger.log(logging.DEBUG, 'result: {}'.format(result))
        return result
    return inner

if __name__ == '__main__':
    from lewas.tokenizers import grouper
    lines = [ '1* 2+3',
              '4 5* 6+',
              '7+ 8 9*' ]

    sep = re.compile(r'(?:([{}])\s*|\s+)'.format('*+'))    
    
    sp = split_parser(splitre=sep)

    print(sp)
