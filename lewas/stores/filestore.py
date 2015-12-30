import logging

from sys import stdout

logger = logging.getLogger(__name__)

class FileStore():
    def __init__(self, **kwargs):
        self.stream = kwargs.get('stream', stdout)
    
    def post(self, measurements, **kwargs):
       logger.log(logging.DEBUG, 'posting')
       [ self.stream.write(repr(m) + '\n') for m in measurements ] 
