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

def coerced_dict(d):
    return { k: coerce(v) for k,v in dict(d).items() }

class Config():
    def __init__(self, config="../config"):
        c = ConfigParser.RawConfigParser()
        c.read(os.path.abspath(config))
        self._config = c

        self.site = c.get("main", "site")
        self.datastore = self.__getattr__(c.get("main", "datastore"))

    def __str__(self):
        return str(self._config)

    def get(self, label, default=None):
        return self._config.get(label, default)
    
    @property
    def datastore(self):
        return coerced_dict(self._config.items(self._config.get('main', 'datastore')))
    
    def __getattr__(self, attr):
        return coerced_dict(self._config.items(attr))
