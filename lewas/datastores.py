import json, urllib, urllib2, ConfigParser, os, sys
from datetime import datetime
import pytz

TZ = pytz.timezone('US/Eastern') # TODO: move to config parameter
    
class IOPrinter():
    """A datastore for debug and testing purposes: prints measurements to stdout"""

    def post(self, measurements, **kwargs):
        print(measurements)

class leapi():
    """Datastore for leapi application/json"""

    def __init__(self, config="../config"):
        c = ConfigParser.RawConfigParser()
        c.read(os.path.abspath(config))
        c = {i[0]: i[1] for i in c.items("leapi")}
        self.host = c.get("host")
        self.password = c.get("password")
        self.storage = os.path.abspath(c.get("storage", "../requests"))
        if not os.path.exists(self.storage):
            os.makedirs(self.storage)
        self.endpoint = c.get("endpoint", "/observations")
        
    def post(self, measurements, **kwargs):
        site_id = None
        if 'site_id' in kwargs:
            site_id = kwargs['site_id']

        for m in measurements:
            if not hasattr(m, 'value'):
                print("Error: {} has no attribute 'value'".format(m))
                continue
            if not hasattr(m, 'unit'):
                print("Error: {} has no attribute 'unit'".format(m))
                continue
            for a in ["unit", "metric"]: #don't check "value" because that breaks if it's 0
                if not getattr(m,a):
                    print ("Error: m.{} ({}) is not truthy".format(a, getattr(m,a)))
                    continue
                       
            d = {a: getattr(m, a) for a in ["unit", "value", "metric"]}
            
            d['units'] = dict(abbv=d['unit'])
            if not isinstance(d['metric'], tuple) or len(d['metric']) != 2:
                print("Error: d['metric'] ({}) is not a 2-tuple".format(d['metric']))
                continue
            d['metric'] = dict(name=d['metric'][1], medium=d['metric'][0])
            d['datetime'] = str(datetime.now(TZ)) #TODO: move this to Measurement constructor
            o = getattr(m, 'offset', () )
            if hasattr(o, '__iter__') and len(o) > 0:
                d['offset'] = dict(zip( ('type','value'), o))
	    stderr = getattr(m, 'stderr', None)
            if stderr != None:
		d['stderr'] = stderr
            #d['instrument'] = dict(name=m.instrument)
            if self.password:
                d['magicsecret'] = self.password #FIXME: move to submission step
            m_site_id = m.station if m.station else site_id
            url = urllib2.Request(self.host + urllib2.quote('/sites/' + m_site_id + '/instruments/' \
                                  + m.instrument + self.endpoint), json.dumps(d, indent=4),
                                  {'Content-Type': 'application/json'})
            try:
                response = urllib2.urlopen(url)
            except urllib2.HTTPError as e:
                print("{}\n\trequest: {}".format(e, json.dumps(d)))
                response = None
            except urllib2.URLError as e:
                print("{}\n\turl: {}".format(e, url))
                response = None
            sys.stdout.flush()
            #print(response)
