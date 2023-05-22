#get GEOS-5 data
#Author: Quance Wu
#date :2020/11/27
import os,sys,re
import numpy as np
import ftplib
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
    daysago = -1
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(base_dir)
DataTime = datetime.today()+ timedelta(days=daysago)
Nowdatetime = DataTime.strftime("%Y-%m-%d 0000")
DataTime = datetime.strptime(Nowdatetime, "%Y-%m-%d %H%M")
# DataTime = datetime.strptime("2020-09-23 0000", "%Y-%m-%d %H%M")
starttime = datetime(2020,9,14)
endtime = datetime(2020,9,17)
starttime = DataTime
endtime = DataTime+timedelta(days=1)
day_list = np.array([dt for dt in datetime_range(starttime, endtime, {'days': 1})])
flist = ['#data from {} to {}'.format(starttime.strftime('%Y-%m-%d'),endtime.strftime('%Y-%m-%d'))]
for i,ida in enumerate(day_list):
    YEAR = ida.strftime('%Y')
    m = ida.strftime('%m')
    d = ida.strftime('%d')
    h = ida.strftime('%H')
    print(ida)
    starttime = ida+timedelta(days=1)
    endtime = DataTime+timedelta(days=8)
    datafilelist = np.array([dt for dt in datetime_range(starttime, endtime, {'hours': 6})])
    if i%1 == 0:
        initdate = ida
        URL = 'https://portal.nccs.nasa.gov/datashare/gmao/geos-fp/forecast/Y'+YEAR+'/M'+m+'/D'+d+'/H'+h+'/'
        flag=1
        errornum = 0
        mode = 0
        while flag:
            try:
                r = requests.get(URL,timeout = 180)
                print(r.status_code)
                if r.status_code == requests.codes.ok:
                    print("OK")
                # print(r.text)
                html_str = r.text
                # parsing data
                data = pq(html_str)
                poster_selector = "body"
                dd=data(poster_selector).text()
                files = dd.split()
                flag=0
            except requests.exceptions.RequestException as e:
                print('error')
                print(e)
                errornum += 10
                if errornum == 2:
                    flag = 0
                    mode = 1
                else:
                    flag=1
        # https://portal.nccs.nasa.gov/datashare/gmao/geos-fp/forecast/Y2020/M09/D24/H00/GEOS.fp.fcst.inst1_2d_hwl_Nx.20200924_00+20200923_2200.V01.nc4
        # /GEOS.fp.fcst.inst1_2d_hwl_Nx.
        # https://portal.nccs.nasa.gov/datashare/gmao/geos-fp/forecast/Y2020/M09/D24/H00/GEOS.fp.fcst.inst3_3d_asm_Np.20200924_00+20200924_0000.V01.nc4
    for j,j_3hr in enumerate(datafilelist):
        print(j_3hr)
        if mode == 0:
            files_GEOS_inst1_2d_hwl_Nx = [f for f in files if re.match(r"GEOS.fp.fcst.inst1_2d_hwl_Nx.{init}\+{forecast}.V\d+.nc4"\
                                    .format(init=initdate.strftime("%Y%m%d_%H"),forecast=j_3hr.strftime("%Y%m%d_%H%M")),f)]
            files_GEOS_inst1_3d_asm_Np = [f for f in files if re.match(r"GEOS.fp.fcst.inst3_3d_asm_Np.{init}\+{forecast}.V\d+.nc4"\
                                    .format(init=initdate.strftime("%Y%m%d_%H"),forecast=j_3hr.strftime("%Y%m%d_%H%M")),f)]
            print(files_GEOS_inst1_2d_hwl_Nx)
            print(files_GEOS_inst1_3d_asm_Np)
            if files_GEOS_inst1_2d_hwl_Nx:
                flist.append('https://portal.nccs.nasa.gov/datashare/gmao/geos-fp/forecast/Y'+YEAR+'/M'+m+'/D'+d+'/H'+h+'/'+files_GEOS_inst1_2d_hwl_Nx[0])
            if files_GEOS_inst1_3d_asm_Np:
                flist.append('https://portal.nccs.nasa.gov/datashare/gmao/geos-fp/forecast/Y'+YEAR+'/M'+m+'/D'+d+'/H'+h+'/'+files_GEOS_inst1_3d_asm_Np[0])
        elif mode == 1:
            flist.append('https://portal.nccs.nasa.gov/datashare/gmao/geos-fp/forecast/Y'+YEAR+'/M'+m+'/D'+d+'/H'+h+'/'+r"GEOS.fp.fcst.inst1_2d_hwl_Nx.{init}+{forecast}.V01.nc4"\
                                    .format(init=initdate.strftime("%Y%m%d_%H"),forecast=j_3hr.strftime("%Y%m%d_%H%M")))
            flist.append('https://portal.nccs.nasa.gov/datashare/gmao/geos-fp/forecast/Y'+YEAR+'/M'+m+'/D'+d+'/H'+h+'/'+r"GEOS.fp.fcst.inst3_3d_asm_Np.{init}+{forecast}.V01.nc4"\
                                    .format(init=initdate.strftime("%Y%m%d_%H"),forecast=j_3hr.strftime("%Y%m%d_%H%M")))

# print(flist)
datafolder=['portal.nccs.nasa.gov','datashare','gmao','geos-fp','forecast','Y{}'.format(day_list[0].strftime('%Y')),
                'M{}'.format(day_list[0].strftime('%m')),'D{}'.format(day_list[0].strftime('%d')),
                'H{}'.format(day_list[0].strftime('%H'))]
file_path = os.path.join(base_dir,*datafolder[:])
exist_or_create_dir(file_path)

for i in range(len(flist)//8):
    data_file_path = os.path.join(file_path,'downloadfile_forecast_{}.txt'.format(i+1))
    print(data_file_path)
    with open(data_file_path, 'w') as filehandle:
        filehandle.writelines("%s\n" % place for place in flist[1+i*8:1+i*8+8])


data_file_path = os.path.join(file_path,'downloadfile_forecast.txt')
print(data_file_path)
with open(data_file_path, 'w') as filehandle:
    filehandle.writelines("%s\n" % place for place in flist)