try:
    import RPi.GPIO as GPIO
except RuntimeError as e:
    __NOPI__ = true

class GPIOPinSetup():
    def __init__(self, pinnumber, direction, **kwargs):
        self.channel = pinnumber
        self.direction = direction
        self.value = None if direction == GPIO.IN else kwargs.pop('value', None)
        self.kwargs = kwargs

def inpin(pnumber, **kwargs):
    return GPIOPinSetup(pnumber, GPIO.IN, **kwargs)

def outpin(pnumber, value=None, **kwargs):
    kwargs['value'] = value
    return GPIOPinSetup(pnumber, GPIO.OUT, **kwargs)


