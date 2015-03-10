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

    def __init__(self, config):
        self.config = config
        
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
            if self.config.password:
                d['magicsecret'] = self.config.password #FIXME: move to submission step
            m_site_id = m.station if m.station else site_id
            url = urllib2.Request(self.config.host + urllib2.quote('/sites/' + m_site_id + '/instruments/' \
                                  + m.instrument + self.config.endpoint), json.dumps(d, indent=4),
                                  {'Content-Type': 'application/json'})
            if self.config.sslkey and self.config.sslcrt:
                opener = urllib2.build_opener(HTTPSClientAuthHandler(
                                self.config.sslkey, self.config.sslcrt)).open
            else:
                opener = urllib2.urlopen
            try:
                response = opener(url)
            except urllib2.HTTPError as e:
                print("{}\n\trequest: {}".format(e, json.dumps(d)))
                response = None
            except urllib2.URLError as e:
                print("{}\t{}\n\trequest: {}".format(e, url.get_full_url(), json.dumps(d)))
                response = None
            sys.stdout.flush()
            #print(response)

import urllib2, httplib

class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        # Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)
