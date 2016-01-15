import logging
import threading
import signal
from time import sleep

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    __NOPI__ = True

class GPIOEventAccumulator:
	def __init__(self, channel, **kwargs):
		self._count = 0
		direction = kwargs.pop('direction', GPIO.RISING)
		self._mode = kwargs.pop('mode', 'event')
		self._channel = channel
		self._interval = kwargs.pop('interval', 1/40.0)
		self._t1 = None
		self._stop = False
		if self._mode == 'event':
			logging.info('using event detection mode')
			GPIO.add_event_detect(channel, direction, callback=self._accumulate, **kwargs) 
		else:
			logging.info('using threading and polling')
			for sig in [signal.SIGINT, signal.SIGTERM]:
                		signal.signal(sig, self._signal_handler)
			self._t1 = threading.Thread(target=self.run)

	def __enter__(self):
		if self._t1 is not None:
			self._t1.start()
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		if self._t1:
			self._stop = True
			self._t1.join()
		if self._mode == 'event':
			GPIO.remove_event_detect(self._channel)
		GPIO.cleanup()

	def _accumulate(self, event):
		logging.debug('GPIOEventAccumulator._accumulate()')
		self._count = self._count + 1

	@property
	def count(self):
		this_count, self._count = self._count, 0
		return this_count

	@property
	def is_alive(self):
		return self._mode == 'event' or not self._stop

	def run(self):
		last_tick, this_tick = 0, 0
		self._stop = False
		logging.debug('entering run loop with interval {}s'.format(self._interval))
		while not self._stop:
			last_tick, this_tick = this_tick, GPIO.input(self._channel)
			if last_tick == 0 and this_tick == 1:
				self._accumulate()
			sleep(self._interval)

	def _signal_handler(self, sig, frame):
		logging.debug('received signal {}'.format(sig))
		self._stop = True
		
