import usb.core
import usb.util

class UsbReader:
	def __init__(idVendor,idProduct,endpoint,maxReadLength=100):
		self.idVendor = idVendor
		self.idProduct = idProduct
		self.endpoint = endpoint
		self.maxReadLength = maxReadLength
		self.dev = usb.core.find(idVendor=self.idVendor,idProduct=self.idProduct)

	def read():
		return ''.join([ char(x) for x in dev.read(self.endpoint, self.maxReadLength) ])
