from typing import Dict

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
