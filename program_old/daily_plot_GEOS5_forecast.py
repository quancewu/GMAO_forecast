######################################################################
#plot GEOS-5 for Forecast                                            #
#author: Quance Wu                                                   #
#date: 2020/11/02                                                    #
#email: quance@g.ncu.edu.tw                                          #
######################################################################
import os,sys,re
import subprocess
import numpy as np
from datetime import datetime,timedelta
from lib.plot_forecast_2 import plot_data,serial_data_plot_storage
from lib.util import datetime_range,exist_or_create_dir
from multiprocessing import Pool

print('execut python3 {}'.format(*sys.argv[:]))
if len(sys.argv) > 1:
    daysago = -int(sys.argv[1])
else:
    # daysago = -2
    daysago = -5
base_dir = os.path.dirname(os.path.abspath(__file__))
print(base_dir)
DataTime = datetime.today() + timedelta(days=daysago)
Nowdatetime = DataTime.strftime("%Y-%m-%d 0000")
DataTime = datetime.strptime(Nowdatetime, "%Y-%m-%d %H%M")
# force to set time
#========================================================================
# DataTime = datetime.strptime("2020-10-06 0000", "%Y-%m-%d %H%M")
# starttime = datetime(2020,10,1)
# endtime = datetime(2020,11,1)
starttime = DataTime
endtime = DataTime+timedelta(days=1)
day_list = np.array([dt for dt in datetime_range(starttime, endtime, {'days': 1})])
flist = ['#data from {} to {}'.format(starttime.strftime('%Y-%m-%d'),endtime.strftime('%Y-%m-%d'))]
Pressure=[1000,925,850,700,500]
title=['1000hPa','925hPa','850hPa','700hPa','500hPa']
data_type=['Total AOD','Smoke','Dust','Sulfate','Sea salt']
Sites = ["NCU","Mt.Lulin","Dongsha","Tai Ping",
        "Son La","Doi Ang Khang","Chiang Mai","Bangkok",
            "Palangkaraya","Jambi","jakarta"]
for i,initdate in enumerate(day_list):
    print(i,initdate)
    starttime = initdate+timedelta(days=1)
    endtime = DataTime+timedelta(days=8)
    forecast_list = np.array([dt for dt in datetime_range(starttime, endtime, {'hours': 6})])
    # plot_data(Pressure[0:1],initdate,forecast_list[0],title[0:1],data_type[0:1])
    with Pool(processes=32) as p:
        for j,forecasttime in enumerate(forecast_list):
            print('    forecast time {}'.format(forecasttime))
            p.apply_async(plot_data,(Pressure,initdate,forecasttime,title,data_type))
        p.close()
        p.join()

    #csv file gerenrate
    serial_data_plot_storage(initdate=initdate,forecast_range=7,data_type_list=data_type,sites=Sites)

    ## cp file to forecast Nas 
    # print("start cp file")
    # cp_time = initdate+timedelta(days=1)
    # cp_year = cp_time.strftime('%Y')
    # cp_month = cp_time.strftime('%m')
    # cp_day = cp_time.strftime('%d')
    # output_folder_list=['/data','forecast_img','geos5','{}'.format(cp_time.strftime('%Y')),
    #             '{}'.format(cp_time.strftime('%m'))]
    # output_folder = os.path.join(*output_folder_list[:])
    # exist_or_create_dir(output_folder)
    # output_folder_ftp_list=['/data','forecast_img','geos5','{}'.format(cp_time.strftime('%Y')),
    #             '{}'.format(cp_time.strftime('%m'))]
    # output_folder_ftp = os.path.join(*output_folder_ftp_list[:])
    # exist_or_create_dir(output_folder_ftp)
    
    # process_cp = subprocess.run(["cp", "-r", "/GEOS5/output_forecast/{cp_year}/{cp_month}/{cp_day}/.".format(cp_year=cp_year,cp_month=cp_month,cp_day=cp_day),
    #             "/data/forecast_img/geos5/{cp_year}/{cp_month}/{cp_day}/".format(cp_year=cp_year,cp_month=cp_month,cp_day=cp_day)])
    # print("end if copying files")