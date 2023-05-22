from datetime import date,datetime,timedelta
import os
def datetime_range(start, end, delta):
    current = start
    if not isinstance(delta, timedelta):
        delta = timedelta(**delta)
    while current < end:
        yield current
        current += delta

def append_value(dict_obj,key,value):
    if key not in dict_obj:
        dict_obj.update({key: [value]})
    elif key in dict_obj:
        if not isinstance(dict_obj[key], list):
            dict_obj[key] = [dict_obj[key]]
        dict_obj[key].append(value)
    else:
        dict_obj[key] = value

def exist_or_create_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    return path