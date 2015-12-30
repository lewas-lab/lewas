import logging

from time import sleep

logger = logging.getLogger(__name__)

def fileSource(file_name, **kwargs):
    delay = kwargs.get('delay', 0)
    def reader():
        with open(file_name, 'r') as f:
            logger.log(logging.DEBUG, 'opened file {} for reading'.format(file_name))
            for line in f:
                logger.log(logging.DEBUG, 'yielding: {}'.format(line.strip()))
                yield line
                sleep(delay)
    return reader()

if __name__ == '__main__':
    import argparse
    import re

    parser = argparse.ArgumentParser('file source test script')
    parser.add_argument('file', help='name of file to open')

    args = parser.parse_args()

    fs = fileSource(args.file)
    sep = re.compile(r'([\s#]+)')

    def splitter(iterable):
        for t in [ sep.split(it) for it in iterable ]:
            yield t

    for line in splitter(fs):
        print('line: {}'.format(line))

