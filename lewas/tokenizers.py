from itertools import tee,izip,cycle

def grouper(iterable, n):
    "Collect data into minimum-length chunks or blocks"
    # grouper('ABCDEFG', 3) --> ABC DEF
    args = [iter(iterable)] * n
    return izip(*args)

def splitGroupTokenizer(token_sep, n=1, wrapper=lambda x: x):
    def tokenizer(datasource):
        for line in datasource:
            tokens = token_sep.split(line)
            for g in grouper(tokens, n):
                yield wrapper(g)
    return tokenizer


