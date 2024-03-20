from typing import Dict
from functools import reduce

def get_path(data: Dict, *keys):
    '''
    Retrieve a nested series of keys from a JSON

    e.g. `get_path(foo, 'bar', 'baz')` will return `foo['bar']['baz']`
    '''

    if data == None or not len(keys):
        return None

    child = data.get(keys[0], None)

    if child == None:
        return child

    if len(keys) == 1:
        return child

    return get_path(child, *keys[1:])

def has_path(object, *keys):
    '''
    Checks if a nested series of keys is defined in a JSON

    e.g. `has_path(foo, 'bar', 'baz') returns True if
    `foo['bar']['baz']` will not raise KeyErrors.
    '''

    def get_with_fallback(obj, key): return obj.get(key, dict())
    deepest = reduce(get_with_fallback, keys[:-1], object)
    return keys[-1] in deepest
