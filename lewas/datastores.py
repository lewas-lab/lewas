import json, urllib, urllib2
from datetime import datetime
import pytz

TZ = pytz.timezone('US/Eastern') # TODO: move to config parameter
    
class IOPrinter():
    """A datastore for debug and testing purposes: prints output to standard stream"""

    def post(self, measurements, **kwargs):
        print(measurements)

class RESTPOST():
    """Prototype HTTP POST datastore (format experimental, no data caching)"""

    def post(self, measurements, **kwargs):
        for m in measurements:
            d = {a: getattr(m, a) for a in ["unit", "value", "metric"]}
            path = "/{}/{}".format(m.station, m.instrument)
            path = "http://127.1:5050" + urllib.pathname2url(path)
            url = urllib2.Request(path, json.dumps(d, indent=4),
                            {'Content-Type': 'application/json'})
            try:
                response = urllib2.urlopen(url)
            except urllib2.HTTPError as e:
                print(e)
                response = None
            print(response)

class leapi():
    """Quick and dirty datastore for leapi application/json+lewas"""

    def __init__(self, host="http://lewaspedia.enge.vt.edu:8080"):
        self.host = host
        
    def post(self, measurements, **kwargs):
        site_id = None
        if 'site_id' in kwargs:
            site_id = kwargs['site_id']
        endpoint = "/observations"   # TODO: get from config?

        for m in measurements:
            if not hasattr(m, 'value'):
                print("Error: {} has no attribute 'value'".format(m))
                continue
            if not hasattr(m, 'unit'):
                print("Error: {} has no attribute 'unit'".format(m))
                continue
            for a in ["unit", "metric"]: #don't check value because that breaks if it's 0
                if not getattr(m,a):
                    print ("Error: m.{} ({}) is not truthy".format(a, getattr(m,a)))
                    continue
                       
            d = {a: getattr(m, a) for a in ["unit", "value", "metric"]}
            
            d['units'] = dict(abbv=d['unit'])
            if not isinstance(d['metric'], tuple) or len(d['metric']) != 2:
                print("Error: d['metric'] ({}) is not a 2-tuple".format(d['metric']))
                continue
            d['metric'] = dict(name=d['metric'][1], medium=d['metric'][0])
            #d['site'] = dict(id=m.station)
            m_site_id = m.station if m.station else site_id
            d['datetime'] = str(datetime.now(TZ))
            o = getattr(m, 'offset', () )
            if hasattr(o, '__iter__') and len(o) > 0:
                d['offset'] = dict(zip( ('type','value'), o))
	    stderr = getattr(m, 'stderr', None)
            if not stderr == None:
		d['stderr'] = stderr
            #d['instrument'] = dict(name=m.instrument)
            d['magicsecret'] = "changethisafterssl" #FIXME: move to config option
            url = urllib2.Request(self.host + urllib2.quote('/sites/' + m_site_id + '/instruments/' + m.instrument + endpoint), json.dumps(d, indent=4),
                                  {'Content-Type': 'application/json'})
            try:
                response = urllib2.urlopen(url)
            except urllib2.HTTPError as e:
                print("{}\n\trequest: {}".format(e, json.dumps(d)))
                response = None
            except urllib2.URLError as e:
                print("{}\n\turl: {}".format(e, url))
                response = None
            #print(response)
