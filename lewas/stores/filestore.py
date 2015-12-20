class FileStore():
    def __init__(self, config, **kwargs):
        self.stream = kwargs.get('stream', congig.get('stream', sys.stdout))
    
    def post(self, measurements, **kwargs):
       [ self.stream.write(str(m) + '\n') for m in measurements ] 
