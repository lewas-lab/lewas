import logging

logger = logging.getLogger(__name__)

def is_indexable_but_not_string(obj):
    return not hasattr(obj, "strip") and hasattr(obj, "__iter__")

