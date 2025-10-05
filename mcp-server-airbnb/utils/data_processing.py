"""
Data processing utilities for cleaning and filtering data
"""


def clean_object(obj):
    """Remove null/undefined values and __typename fields"""
    if isinstance(obj, dict):
        keys_to_delete = []
        for key, value in obj.items():
            if value is None or key == "__typename":
                keys_to_delete.append(key)
            elif isinstance(value, (dict, list)):
                clean_object(value)
        for key in keys_to_delete:
            del obj[key]
    elif isinstance(obj, list):
        for item in obj:
            clean_object(item)
    return obj


def pick_by_schema(obj, schema):
    """Filter object to only include fields specified in schema"""
    if not isinstance(obj, dict) or obj is None:
        return obj

    if isinstance(obj, list):
        return [pick_by_schema(item, schema) for item in obj]

    result = {}
    for key, rule in schema.items():
        if key in obj:
            if rule is True:
                result[key] = obj[key]
            elif isinstance(rule, dict):
                result[key] = pick_by_schema(obj[key], rule)
    return result


def flatten_arrays_in_object(input_obj, in_array=False):
    """Flatten nested arrays and objects into readable strings"""
    if isinstance(input_obj, list):
        flat_items = [flatten_arrays_in_object(item, True) for item in input_obj]
        return ', '.join(str(item) for item in flat_items)
    elif isinstance(input_obj, dict):
        if in_array:
            values = [flatten_arrays_in_object(v, True) for v in input_obj.values()]
            return ': '.join(str(v) for v in values)
        else:
            result = {}
            for key, value in input_obj.items():
                result[key] = flatten_arrays_in_object(value, False)
            return result
    else:
        return input_obj
