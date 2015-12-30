from itertools import tee,izip,izip_longest,cycle

def _grouper(iterable, n):
    "Collect data into minimum-length chunks or blocks"
    # grouper('ABCDEFG', 3) --> ABC DEF GNoneNone
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=None, *args)

def grouper(n):
    def inner(it):
        return _grouper(it, n)
    return inner

def splitGroupTokenizer(token_sep, n=1, wrapper=lambda x: x):
    def tokenizer(datasource):
        for line in datasource:
            tokens = token_sep.split(line)
            for g in _grouper(tokens, n):
                yield wrapper(g)
    return tokenizer


