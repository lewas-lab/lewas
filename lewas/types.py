class QualifiedFloat():
    def __init__(self, value, qualifier, decorations):
        self.value = float(value)
        self.qualifier = qualifier
        self.decorations = decorations

    def __float__(self):
        return self.value

    def __repr__(self):
        return '<QualifiedFloat: {} {}>'.format(str(self.value), str(self.flags))

    def __str__(self):
        return str(self.value)

    @property
    def flags(self):
        try:
            return [ self.decorations[self.qualifier][0] ]
        except KeyError:
            return []

def decorated_float(decorations):
    def inner(value):
        return QualifiedFloat(value[0], value[1], decorations=decorations)
    return inner
