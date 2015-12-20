import ConfigParser, os

def coerce(val):
	try:
		return int(val)
	except ValueError:
		pass
	try:
		return float(val)
	except ValueError:
		pass
	return val

class Config():
    def __init__(self, config="../config"):
        c = ConfigParser.RawConfigParser()
        c.read(os.path.abspath(config))
	self._config = c
        d = {i[0]: i[1] for i in c.items("leapi")}
        for attr in ['host','password','sslkey','sslcrt',
                ('storage','../requests'),
                ('endpoint','/observations')]:
            if hasattr(attr, '__iter__'):
                setattr(self, attr[0], d.get(attr[0], attr[1]))
            else:
                setattr(self, attr, d.get(attr))

        self.storage = os.path.abspath(self.storage)
        if not os.path.exists(self.storage):
            os.makedirs(self.storage)

        self.site = c.get("main", "site")
	self.instruments = {}

	for section in [ s for s in c.sections() if s not in ['main','leapi'] ]:
		#setattr(self, section, {attr: coerce(val) for (attr,val) in c.items(section) })
		self.instruments[section] = {attr: coerce(val) for (attr,val) in c.items(section) }
		#print('adding attributes for section {}'.format(section))
		#[ setattr(self, attr, val) for (attr,val) in c.items(section) ]
    def __str__(self):
	return str(self._config)

    #def __getattr__(self, attr):
    #	print('items({}): {}'.format(attr, self._config.items(attr)))
