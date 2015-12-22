from flask_restful import Resource, fields, marshal_with
from lewas.exceptions import ConfigError

class MetricField(fields.Raw):
    def format(self, value):
        return { 'name': value[1], 'medium': value[0] }

class Method(fields.Raw):
    def output(self, key, obj):
        return 1

fields = {
        'value': fields.Float,
        'units': { 'abbv': fields.String(attribute='unit') },
        'metric': MetricField,
        'datetime': fields.DateTime(dt_format='iso8601'),
        'stderr': fields.Float,
        'method_id': Method,
        'flags': fields.List(fields.String)
        }

def leapiStore(**kwargs):
    from lewas.stores import RESTStore
    try:
        return RESTStore(fields=fields, **kwargs)
    except ConfigError as e:
        raise ConfigError('leapiStorage: ' + e.message)
