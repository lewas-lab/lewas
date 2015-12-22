import logging

from sys import stdout

class FileStore():
    def __init__(self, **kwargs):
        self.stream = kwargs.get('stream', stdout)
    
    def post(self, measurements, **kwargs):
       logging.info('posting to FileStore')
       [ self.stream.write(repr(m) + '\n') for m in measurements ] 
