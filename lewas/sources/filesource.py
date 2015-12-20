def fileSource(config, **kwargs):
    file_name = kwargs.get('file', config.get('file', None))
    delay = kwargs.get('delay', config.get('delay', 0))
    def reader():
        with open(file_name, 'r') as f:
            for line in f:
                yield f
                sleep(delay)
    return reader
