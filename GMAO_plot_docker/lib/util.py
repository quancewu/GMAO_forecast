import os
from pathlib import Path, PurePath
import yaml
from datetime import datetime,timedelta
import pandas as pd
import numpy as np
import urllib3
import json


def send_message_to_telegram(message):
    http = urllib3.PoolManager()
    data = {
        'message': message
        }
    encoded_data = json.dumps(data).encode('utf-8')
    r = http.request(
            'POST',
            'https://quance.tornadoedge.app/hook/apiv1?group=group_01',
            body=encoded_data,
            headers={'Content-Type': 'application/json'}
        )
    print(r.status)

def exist_or_create_dir(path):
    if type(path) is str:
        if not os.path.isdir(path):
            os.makedirs(path)
        return path
    else:
        return True if path.exists() else path.mkdir(parents=True)


class File:
    base_dir = Path(__file__).parent.resolve()
    base_dir = Path(*PurePath(base_dir).parts[:-1])
    log_dir = base_dir/'log_file'
    fig_dir = base_dir/'fig'
    save_dir = base_dir/'data_file'
    config_dir = base_dir/'config'
    # nas_dir = Path('/mnt/nas/CALab/Data/EPA/data/NetCDF/L1_newdataset')
    with open(config_dir/'config.yaml', 'r', encoding='utf-8') as f:
        config_file = yaml.load(f, Loader=yaml.FullLoader)
    with open(config_dir/'color.yaml', 'r', encoding='utf-8') as f:
        epa_color_yaml = yaml.load(f, Loader=yaml.FullLoader)

    # with open(config_dir/'data_file_path.yaml', 'w', encoding='utf-8') as f:
    #     yaml.dump(config_file, f, sort_keys=False)
    '''
        if you want to add colormap and save automatically in epa_color.ymal file
        please uncomment below and set a new dictionary key to saving color index.
    '''
    # epa_color = ['#9cff9c', '#41FF00', '#ffff00', '#FFCF00', '#FF9A00',
    #              '#CD6600', '#FF0000', '#990000', '#ba55d3', '#A020F0']
    # epa_color_yaml = dict(epa_color=epa_color)
    # with open(config_dir/'epa_color.yaml', 'w', encoding='utf-8') as f:
    #     yaml.dump(epa_color_yaml, f, sort_keys=False)

    data_dir = Path(config_file['data_path'])
    # file_dir_list = config_file['station']
    # used_list = config_file['used_list']
    # para_index = config_file['para_index']
    # epa_color = epa_color_yaml['epa_color']
    # epa_color = list(zip(np.linspace(0, 1, len(epa_color)), epa_color))
    exist_or_create_dir(base_dir)
    exist_or_create_dir(config_dir)
    exist_or_create_dir(log_dir)
    exist_or_create_dir(fig_dir)
    exist_or_create_dir(save_dir)


# class Station_info:
#     header = ['station', 'lon', 'lat', 'height', 'note']
#     ch = pd.read_csv(
#         File.config_dir/'EPA_location_Ch_big5.csv', encoding='big5')
#     ch.columns = header
#     en = pd.read_csv(File.config_dir/'EPA_location_En.csv', encoding='big5')
#     en.columns = header


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

# def exist_or_create_dir(path):
#     if not os.path.isdir(path):
#         os.makedirs(path)
#     return path

class sites_data:
    information = {
        "NCU":{
            'lat':24.968,
            'lon':121.188,
            'timezone':8
        },
        "Mt.Lulin":{
            'lat':23.469,
            'lon':120.874,
            'timezone':8
        },
        "Dongsha":{
            'lat':20.699,
            'lon':116.729,
            'timezone':8
        },
        "Tai Ping":{
            'lat':10.376,
            'lon':114.362,
            'timezone':8
        },
        "Son La":{
            'lat':21.332,
            'lon':103.905,
            'timezone':7
        },
        "Doi Ang Khang":{
            'lat':19.932,
            'lon':99.045,
            'timezone':7
        },
        "Chiang Mai":{
            'lat':18.813,
            'lon':98.987,
            'timezone':7
        },
        "Bangkok":{
            'lat':13.749,
            'lon':100.518,
            'timezone':7
        },
        "Palangkaraya":{
            'lat':-2.199,
            'lon':113.893,
            'timezone':7,
        },
        "Jambi":{
            'lat':-1.581,
            'lon':103.404,
            'timezone':7,
        },
        "jakarta":{
            'lat':-6.193,
            'lon':106.845,
            'timezone':7,
        },
    }
