class AttrParser():
    """An AttrParser does not generate new Measurement objects,
       instead it modifies attributes of existing measurement objects.
       This is useful for sensors that produce properties of measurements
       as separate parsed fields, such as standard deviation estimates, flags, etc."""

    def __init__(self,typef,attr,pred):
        self.typef = typef
        self.attr = attr
        if not hasattr(pred, '__call__'):
            raise RuntimeError("predicate must be callable")
        self.pred = pred

    def __call__(self, measurements, value):
        #print("setting '{}' to '{}'".format(self.attr, value))
        for m in measurements:
            if self.pred(m):
                setattr(m, self.attr, self.typef(value))
        return measurements

    def __repr__(self):
        return "AttrParser for {0}".format(self.attr)
 
