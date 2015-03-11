import json, urllib, urllib2, ConfigParser, os, sys
import itertools
from datetime import datetime
import pytz
import logging

TZ = pytz.timezone('US/Eastern') # TODO: move to config parameter
    
class IOPrinter():
    """A datastore for debug and testing purposes: prints measurements to stdout"""

    def post(self, measurements, **kwargs):
        print(measurements)

def marshal_observation(m, config, **kwargs):
    if not hasattr(m, 'value'):
        print("Error: {} has no attribute 'value'".format(m))
        return {}
    if not hasattr(m, 'unit'):
        print("Error: {} has no attribute 'unit'".format(m))
        return {}
    for a in ["unit", "metric"]: #don't check "value" because that breaks if it's 0
        if not getattr(m,a):
            print ("Error: m.{} ({}) is not truthy".format(a, getattr(m,a)))
            return {}

    d = {a: getattr(m, a) for a in ["unit", "value", "metric"]}

    d['units'] = dict(abbv=d['unit'])
    if not isinstance(d['metric'], tuple) or len(d['metric']) != 2:
        print("Error: d['metric'] ({}) is not a 2-tuple".format(d['metric']))
        return {}
    d['metric'] = dict(name=d['metric'][1], medium=d['metric'][0])
    d['datetime'] = kwargs.get('datetime', str(datetime.now(TZ))) #TODO: move this to Measurement constructor
    o = getattr(m, 'offset', () )
    if hasattr(o, '__iter__') and len(o) > 0:
        d['offset'] = dict(zip( ('type','value'), o))
        stderr = getattr(m, 'stderr', None)
        if stderr != None:
            d['stderr'] = stderr
            #d['instrument'] = dict(name=m.instrument)
    if config.password:
        d['magicsecret'] = config.password #FIXME: move to submission step

    return d

def mkey(m):
    return (m.station, m.instrument)

class leapi():
    """Datastore for leapi application/json"""

    def __init__(self, config):
        self.config = config
        
    def post(self, measurements, **kwargs):
        site_id = None
        if 'site_id' in kwargs:
            site_id = kwargs['site_id']

        for g,k in itertools.groupby(sorted(measurements, key=mkey), mkey):
            site_id2, instrument_name = g
            url = self.config.host + urllib2.quote('/sites/' + site_id + '/instruments/' \
                                                   + instrument_name + self.config.endpoint)
            now = str(datetime.now(TZ))
            d = [ marshal_observation(m, self.config, datetime=now) for m in k]

            request = urllib2.Request(url, json.dumps(d),
                                  {'Content-Type': 'application/json'})

            #sys.stderr.write("trying {} {}\n\tHeaders: {}".format(request.get_method(), url, request.header_items()))
            logging.info("request of {} observations\n".format(len(d)))
            response = None

            if self.config.sslkey and self.config.sslcrt:
                opener = urllib2.build_opener(HTTPSClientAuthHandler(
                                self.config.sslkey, self.config.sslcrt)).open
            else:
                opener = urllib2.urlopen
            try:
                response = opener(request)
            except urllib2.HTTPError as e:
                print("{}\n\trequest: {}".format(e, json.dumps(d)))
            except urllib2.URLError as e:
                print("{}\n\turl: {}".format(e, request.get_full_url()))
            else:
                logging.info("{}\t{}\n\trequest: {}".format(response.getcode(), request.get_full_url(), json.dumps(d)))
            finally:
                pass
                # TODO, should we log server response?
                #if response is not None:
                logging.info("\tresponse: {}".format(response.read()))
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
