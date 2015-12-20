import serial

def serialSource(config, **kwargs):
    return serial.Serial(config['dev'], config['baud'], **kwargs)
