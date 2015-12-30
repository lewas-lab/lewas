from operator import itemgetter
from itertools import ifilter, imap, takewhile, chain

def taken(iterable, n):
    """take the first N elements of iterable"""
    return imap(itemgetter(1), takewhile(lambda i: i[0] < 2, enumerate(iterable)))

def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)

def compact(iterable):
    """filter out any non-Truthy items (e.g. '', None) of an
    iterable"""
    return filter(lambda m: m, iterable)
