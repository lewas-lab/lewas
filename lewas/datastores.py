import json

class IOPrinter():
    """A datastore for debug and testing purposes: prints output to standard stream"""

    def post(self, measurements, **kwargs):
        print(measurements)

class RESTPOST():
    """Prototype HHTP POST datastore (format experimental, no data caching)"""

    def post(self, measurements, **kwargs):
        dicts = [dict(m) for m in measurements]
        d = {m["metric"]: {a: m[a] for a in ["unit", "value"]} for m in dicts}
        print(json.dumps(d, indent=4))
