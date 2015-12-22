from itertools import imap, takewhile
from operator import itemgetter

def taken(iterable, n):
    return imap(itemgetter(1), takewhile(lambda i: i[0] < 2, enumerate(iterable)))


