class Measurement:
    def __init__(self, value, metric, unit):
        self.value = value
        self.metric = metric
        self.unit = unit

    def __repr__(self):
        return "{2}: {0} {1}".format(self.value, self.unit, self.metric)
