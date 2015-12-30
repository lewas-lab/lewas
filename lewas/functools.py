# see https://mathieularose.com/function-composition-in-python/
def compose(*functions):
    return reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)
