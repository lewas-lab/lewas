class IOPrinter():
    """A datastore for debug and testing purposes: prints output to standard stream"""

    def post(self, measurements, **kwargs):
        for m in measurements:
            print(m)
