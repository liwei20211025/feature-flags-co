
import json


def check_format(input={}, key=None, fmt=None, values_range=[]):
    value = input.get(key, None)
    is_valid = False
    if value :
        if type(value) is fmt :
            if values_range:
                if value in values_range :
                    is_valid = True
            else:
                is_valid = True
    return is_valid


def encode(value):
    return str.encode(json.dumps(value))


def decode(value):
    if isinstance(value, bytes):
        data = json.loads(value.decode())
    elif isinstance(value, str):
        data = json.loads(value)
    else:
        data = value
    return data