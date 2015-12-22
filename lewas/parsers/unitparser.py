from lewas.models import Measurement

class UnitParser():
    def __init__(self, typef, metric, units, **kwargs):
        self.typef = typef
        self.metric = metric
        self.units = units
        self.instrument = kwargs['instrument'] if 'instrument' in kwargs else None
        #self.sensor = kwargs['sensor']
        self.site = kwargs['site'] if 'site' in kwargs else None
        self.offset = kwargs['offset'] if 'offset' in kwargs else None
        
    @property
    def units(self):
        return self.units

    @property
    def metric(self):
        return self.metrics

    def __call__(self,value):
        v = self.typef(value)
        kwargs = { 'instrument': self.instrument,
                    'station': self.site,
                    'offset': self.offset,
                    'flags': getattr(v,'flags',None)
                 }
        return Measurement(str(v),self.metric,self.units, **kwargs)

    def __repr__(self):
        return "unitParser ({})".format((self.typef,self.metric,self.units,self.instrument,self.site))


