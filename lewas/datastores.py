import json, urllib, urllib2, ConfigParser, os, sys, httplib
import itertools
import pytz
import logging

class IOPrinter():
    """A datastore for debug and testing purposes: prints measurements to stdout"""

    def post(self, measurements, **kwargs):
        print(measurements)

def marshal_observation(m, config, **kwargs):
    if not hasattr(m, 'value'):
        logging.error("Error: {} has no attribute 'value'".format(m))
        return {}
    if not hasattr(m, 'unit'):
        logging.error("Error: {} has no attribute 'unit'".format(m))
        return {}
    for a in ["unit", "metric"]: #don't check "value" because that breaks if it's 0
        if not getattr(m,a):
            logging.error("Error: m.{} ({}) is not truthy".format(a, getattr(m,a)))
            return {}

    d = {a: getattr(m, a) for a in ["unit", "value", "metric"]}

    d['units'] = dict(abbv=d['unit'])
    if not isinstance(d['metric'], tuple) or len(d['metric']) != 2:
        logging.error("Error: d['metric'] ({}) is not a 2-tuple".format(d['metric']))
        return {}
    d['metric'] = dict(name=d['metric'][1], medium=d['metric'][0])
    d['datetime'] = m.time
    o = getattr(m, 'offset', () )

    if hasattr(o, '__iter__') and len(o) > 0:
        d['offset'] = dict(zip( ('type','value'), o))

    d['stderr'] = getattr(m, 'stderr', None)
        
    d['method_id'] = 1
    
    if config.password:
        d['magicsecret'] = config.password #FIXME: move to submission step

    return d

mkey = lambda m: (m.station, m.instrument)

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
            d = [ marshal_observation(m, self.config, datetime=m.time) for m in k]

            request = urllib2.Request(url, json.dumps(d),
                                  {'Content-Type': 'application/json'})

            logging.info("request of {} observations\n".format(len(d)))
            submitRequest(d, request, self.config)

def submitRequest(d, request, config):
    #config is ONLY used for authentication
    #FIXME: should not be passing in d, instead extract it from request (mw investigate how to do this)
    response = None
    if config.sslkey and config.sslcrt:
        opener = urllib2.build_opener(HTTPSClientAuthHandler(
                        config.sslkey, config.sslcrt)).open
    else:
        opener = urllib2.urlopen
    try:
        response = opener(request)
    except urllib2.HTTPError as e:
        logging.error("{}\n\trequest: {}".format(e, json.dumps(d)))
    except urllib2.URLError as e:
        logging.error("{}\n\turl: {}".format(e, request.get_full_url()))
    else:
        logging.info("{}\t{}\n\trequest: {}".format(response.getcode(), request.get_full_url(), json.dumps(d)))
    finally:
        if response is not None:
            logging.info("\tresponse: {}".format(response.read()))
    sys.stdout.flush()

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
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert, strict=True)
