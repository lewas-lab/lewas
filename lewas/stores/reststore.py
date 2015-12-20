import hashlib
import itertools
import json
import logging
import pickle
import urllib2
import time
import os

from flask_restful import marshal

def mkey(m):
    return (m.station, m.instrument)

class RESTStore():
    def __init__(self, config, **kwargs):
        self.config = config
        self.host = self.config.host
        self.endpoint = self.config.endpoint
        self.fields = kwargs.get('fields', getattr(config, 'fields', None))

    def post(self, measurements, **kwargs):
        for g,k in itertools.groupby(sorted(measurements, key=mkey), mkey):
            site_id, instrument_name = g
            url = self.host \
                    + urllib2.quote(self.endpoint.format(site_id=site_id, instrument_name=instrument_name))
            
            # marshal measurements into request data
            d = [ marshal(m, self.fields) for m in k ]
            request = urllib2.Request(url, json.dumps(d),
                    {'Content-Type': 'application/json'})
            logging.info('request of {} measurements\n'.format(len(d)))

            submitRequest(request, self.config)

def submitRequest(request, config, saveOnFail=True):
    #config is ONLY used for authentication

    if config.password:
        d = json.loads(request.data)
        for m in d:
            m['magicsecret'] = config.password
        request.data = json.dumps(d)

    response = None
    if config.sslkey and config.sslcrt:
        opener = urllib2.build_opener(HTTPSClientAuthHandler(
                        config.sslkey, config.sslcrt)).open
    else:
        opener = urllib2.urlopen
    success = False
    try:
        response = opener(request)
        success = True
    except urllib2.HTTPError as e:
        # import traceback; traceback.print_exc()
        logging.error("{}\n\trequest: {}".format(e, request.data))
        logging.error("\tresponse: {}".format(e.read()));
    except urllib2.URLError as e:
        logging.error("{}\n\turl: {}\n\trequest: {}".format(e, request.get_full_url(), request.data))
    else:
        logging.info("{}\t{}\n\trequest: {}".format(
                response.getcode(), request.get_full_url(), request.data))
	#TODO: would it be more clear to have the
	#if saveOnFail # here?
    finally:
        if response is not None:
            logging.info("\tresponse: {}".format(response.read()))
        if saveOnFail and not success:
            p = pickle.dumps(request)
            h = hashlib.sha256()
            h.update(p)
            fn = str(int(time.mktime(time.gmtime())))+h.hexdigest() #todo: include instrument
            fn = os.path.join(config.storage, h.hexdigest())
            with open(fn, 'w') as f:
                f.write(p)
    return success

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
