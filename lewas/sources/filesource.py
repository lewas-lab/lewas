import logging

from time import sleep

def fileSource(file_name, **kwargs):
    delay = kwargs.get('delay', 0)
    def reader():
        with open(file_name, 'r') as f:
            logging.info('opened file {} for reading'.format(file_name))
            for line in f:
                logging.debug('yielding line: {}'.format(line.strip()))
                yield line
                sleep(delay)
    return reader()
