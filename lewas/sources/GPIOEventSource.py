import logging
from time import sleep

import RPi.GPIO as GPIO
from GPIOEventAccumulator import GPIOEventAccumulator

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

def first_inpin(pins):
    for pin in pins:
	if pin.direction == GPIO.IN:
		return pin
    raise NoInputPin()

def GPIOEventSource(pin_setup, **kwargs):
    mode = kwargs.pop('mode', GPIO.BOARD)
    direction = kwargs.pop('direction', GPIO.RISING)
    bouncetime = kwargs.pop('bouncetime', 100)
    interval = kwargs.pop('interval', 1)
    detect_method = kwargs.pop('detect_method', 'poll')

    GPIO.setmode(mode)

    for p in pin_setup:
        GPIO.setup(p.channel, p.direction, **p.kwargs)
	logging.debug('setting pin number {} to {} with {}'.format(p.channel, p.direction, p.kwargs))
        if p.direction == GPIO.OUT and p.value is not None:
            	logging.debug('setting pin number {} output to {}'.format(p.channel, p.value))
		GPIO.output(p.channel, p.value)


    input_pin = first_inpin(pin_setup)
    with GPIOEventAccumulator(input_pin.channel, mode=detect_method, direction=direction, bouncetime=bouncetime) as events:
    	while events.is_alive:
        	yield events.count
        	sleep(interval)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    inpin = 24
    output = 26

    pin_setup = [ inpin(24), outpin(26, GPIO.HI) ]

    source = GPIOEventSource(pin_setup, interval=1)
