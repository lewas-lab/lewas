import json, urllib, urllib2
from datetime import datetime

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

    def post(self, measurements, **kwargs):
        endpoint = "/observations"
        host = "http://lewaspedia.enge.vt.edu:8080"

        for m in measurements:
            d = {a: getattr(m, a) for a in ["unit", "value", "metric"]}
            d['units'] = dict(abbv=d['unit'])
            if isinstance(d['metric'], tuple):
                d['metric'] = dict(name=d['metric'][1], medium=d['metric'][0])
            d['site'] = dict(id=m.station)
            d['datetime'] = str(datetime.now())
            d['instrument'] = dict(name=m.instrument)
            url = urllib2.Request(host + endpoint, json.dumps(d, indent=4),
                                  {'Content-Type': 'application/json'})
            print(json.dumps(d))
            try:
                response = urllib2.urlopen(url)
            except urllib2.HTTPError as e:
                print(e)
                response = None
            print(response)
