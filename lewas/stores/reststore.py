import hashlib
import itertools
import json
import logging
import pickle
import urllib2
import time
import os
from collections import namedtuple

from flask_restful import marshal

from lewas.exceptions import ConfigError

logger = logging.getLogger(__name__)

def mkey(m):
    return (m.station, m.instrument)

auth_attrs = ['password', 'sslcrt', 'sslkey']

Auth = namedtuple('Auth', ' '.join(auth_attrs))
class RESTStore():
    def __init__(self, **kwargs):
        self.host = kwargs.get('host') 
        self.endpoint = kwargs.get('endpoint')
        self.fields = kwargs.get('fields', None)
        self.saveOnFail = kwargs.get('saveOnFail', True)
        self.storage = kwargs.get('storage', None) 
        self.auth = Auth( *[ kwargs.get(label, None) for label in auth_attrs ] )
        #try
        if self.saveOnFail:
            try:
                fn = save_request({ 'test': 'to check for write permission' }, self.storage)
                os.remove(fn)
            except AttributeError:
                raise ConfigError('saveOnFail is set but could not find storage information')
            except IOError:
                raise ConfigError('{}: could not write to storage directory, does it even exist?'.format(self.storage))

    def post(self, measurements, **kwargs):
        for g,k in itertools.groupby(sorted(measurements, key=mkey), mkey):
            site_id, instrument_name = g
            url = self.host \
                    + urllib2.quote(self.endpoint.format(site_id=site_id, instrument_name=instrument_name))
            
            logger.log(logging.DEBUG, 'posting to {}'.format(url))
            # marshal measurements into request data
            #for m in k:
            #    logger.log(logging.DEBUG, 'm: {}'.format(m))
            d = [ marshal(m, self.fields) for m in k ]
            try:
                request = urllib2.Request(url, json.dumps(d),
                    {'Content-Type': 'application/json'})
                logger.log(logging.INFO, 'request of {} measurements\n'.format(len(d)))
            except TypeError as e:
                print(e)
                logger.log(logging.ERROR, 'message: {}\nobject: {}'.format(e,d))
            else:
                submitRequest(request, self.auth, storage=self.storage, **kwargs)

def submitRequest(request, auth, saveOnFail=True, **kwargs):
    #config is ONLY used for authentication
    storage = kwargs.get('storage') if saveOnFail else None
    if auth.password:
        d = json.loads(request.data)
        for m in d:
            m['magicsecret'] = auth.password
        request.data = json.dumps(d)

    response = None
    if auth.sslkey and auth.sslcrt:
        opener = urllib2.build_opener(HTTPSClientAuthHandler(
                        auth.sslkey, auth.sslcrt)).open
    else:
        opener = urllib2.urlopen
    success = False
    try:
        response = opener(request)
        success = True
    except urllib2.HTTPError as e:
        # import traceback; traceback.print_exc()
        logger.log(logging.ERROR, "{}\n\trequest: {}".format(e, request.data))
        logger.log(logging.ERROR, "\tresponse: {}".format(e.read()));
    except urllib2.URLError as e:
        logger.log(logging.ERROR, "{}\n\turl: {}\n\trequest: {}".format(e, request.get_full_url(), request.data))
    else:
        logger.log(logging.INFO, "{}\t{}\n\trequest: {}".format(
                response.getcode(), request.get_full_url(), request.data))
	#TODO: would it be more clear to have the
	#if saveOnFail # here?
    finally:
        if response is not None:
            logger.log(logging.INFO, "\tresponse: {}".format(response.read()))
        if saveOnFail and not success:
            save_request(request, storage)
    return success

def save_request(request, storage):
    p = pickle.dumps(request)
    h = hashlib.sha256()
    h.update(p)
    fn = str(int(time.mktime(time.gmtime())))+h.hexdigest() #todo: include instrument
    fn = os.path.join(storage, h.hexdigest())
    with open(fn, 'w') as f:
        f.write(p)
    return fn

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
