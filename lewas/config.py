import ConfigParser, os

class Config():
    def __init__(self, config="../config"):
        c = ConfigParser.RawConfigParser()
        c.read(os.path.abspath(config))
        d = {i[0]: i[1] for i in c.items("leapi")}
        for attr in ['host','password',('storage','../requests'),('endpoint','/observations')]:
            if hasattr(attr, '__iter__'):
                setattr(self, attr[0], d.get(attr[0], attr[1]))
            else:
                setattr(self, attr, d.get(attr))

        self.storage = os.path.abspath(self.storage)
        if not os.path.exists(self.storage):
            os.makedirs(self.storage)

        self.site = c.get("main", "site")
