import json, urllib, urllib2

class IOPrinter():
    """A datastore for debug and testing purposes: prints output to standard stream"""

    def post(self, measurements, **kwargs):
        print(measurements)

class RESTPOST():
    """Prototype HTTP POST datastore (format experimental, no data caching)"""

    def post(self, measurements, **kwargs):
        for m in measurements:
            d = {a: getattr(m, a) for a in ["unit", "value"]}
            path = "http://127.1:5050/{}/{}/{}" \
                   "".format(m.station, m.instrument, m.metric)
            url = urllib2.Request(path, json.dumps(d, indent=4),
                            {'Content-Type': 'application/json+lewas'})
            response = urllib2.urlopen(url)
            print(response)
