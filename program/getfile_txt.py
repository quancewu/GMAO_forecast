import os,sys,re
import numpy as np
import urllib.request
import requests
import time
from pyquery import PyQuery as pq
from datetime import datetime,timedelta
from util import datetime_range

def exist_or_create_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    return path

print('execut python3 {}'.format(*sys.argv[:]))
if len(sys.argv) > 1:
    daysago = -int(sys.argv[1])
else:
    daysago = -2

base_dir = os.path.dirname(os.path.abspath(__file__))
print(base_dir)
DataTime = datetime.today() + timedelta(days=daysago)
Nowdatetime = DataTime.strftime("%Y-%m-%d 0000")
DataTime = datetime.strptime(Nowdatetime, "%Y-%m-%d %H%M")
# DataTime = datetime.strptime("2020-09-15 0000", "%Y-%m-%d %H%M")
starttime = datetime(2020,9,2)
endtime = datetime(2020,9,26)
starttime = DataTime
endtime = DataTime+timedelta(days=1)
day_list = np.array([dt for dt in datetime_range(starttime, endtime, {'days': 1})])
datafilelist = np.array([dt for dt in datetime_range(starttime, endtime, {'hours': 6})])
flist = ['#data from {} to {}'.format(starttime.strftime('%Y-%m-%d'),endtime.strftime('%Y-%m-%d'))]
for i,ida in enumerate(datafilelist):
    YEAR = ida.strftime('%Y')
    m = ida.strftime('%m')
    d = ida.strftime('%d')
    h = ida.strftime('%H')
    print(ida)
    files_inst1_2d_hwl_Nx = f'f5271_fp.inst1_2d_hwl_Nx.{YEAR}{m}{d}_{h}00z.nc4'
    flist.append('https://portal.nccs.nasa.gov/datashare/gmao_ops/pub/fp/das/Y'+YEAR+'/M'+m+'/D'+d+'/'+files_inst1_2d_hwl_Nx)
    files_GEOS_inst3_2d_asm_Nx = f'GEOS.fp.asm.inst3_2d_asm_Nx.{YEAR}{m}{d}_{h}00.V01.nc4'
    flist.append('https://portal.nccs.nasa.gov/datashare/gmao_ops/pub/fp/das/Y'+YEAR+'/M'+m+'/D'+d+'/'+files_GEOS_inst3_2d_asm_Nx)
    files_GEOS_inst3_3d_asm_Np = f'GEOS.fp.asm.inst3_3d_asm_Np.{YEAR}{m}{d}_{h}00.V01.nc4'
    flist.append('https://portal.nccs.nasa.gov/datashare/gmao_ops/pub/fp/das/Y'+YEAR+'/M'+m+'/D'+d+'/'+files_GEOS_inst3_3d_asm_Np)

datafolder=['/data/GEOS5','portal.nccs.nasa.gov','datashare','gmao_ops','pub','fp','das','Y{}'.format(day_list[0].strftime('%Y')),
                'M{}'.format(day_list[0].strftime('%m')),'D{}'.format(day_list[0].strftime('%d'))]
file_path = os.path.join(base_dir,*datafolder[:])
exist_or_create_dir(file_path)
data_file_path = os.path.join(file_path,'downloadfile.txt')
print(data_file_path)
with open(data_file_path, 'w') as filehandle:
    filehandle.writelines("%s\n" % place for place in flist)