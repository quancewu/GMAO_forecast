import os,re,time
import yaml
import logging
import subprocess
import logging.config
import schedule
# import threading
# import queue
from datetime import datetime,timedelta
from lib.plot import plot_data,serial_data_plot_storage
from lib.util import File
from lib.sys_log import logging_config_init,logging_start
from lib.util import exist_or_create_dir,datetime_range
from lib.download_file import download_daily

def run_daily():
    # time_list = [datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=1)]
    st = datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=6)
    et = datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0)-timedelta(days=1)
    time_list = datetime_range(st,et,{'days': 1})
    download_daily(time_list)
    logging.info("start ploting")
    time_list = datetime_range(st,et,{'days': 1})
    for DataTime in time_list:
        forecasttime = datetime.strptime("2022-11-23 0600", "%Y-%m-%d %H%M")
        Pressure=[1000,925,850,700,500]
        title=['1000hPa','925hPa','850hPa','700hPa','500hPa']
        # sulfate SUEXTTAU sea salt SSCMASS sscmass
        data_type=['Total AOD','Smoke','Dust','Sulfate','Sea salt']
        Sites = ["NCU","Mt.Lulin","Dongsha","Tai Ping","Son La","Doi Ang Khang","Chiang Mai","Bangkok"]
        plot_data(pressure_list=Pressure,initdate=DataTime,foreacst_date=forecasttime,title_list=title,data_type_list=data_type)
        serial_data_plot_storage(initdate=DataTime,forecast_range=7,data_type_list=data_type,sites=Sites)
       
        # cp file to forecast Nas 
        logging.info("copy file nas")
        cp_time = DataTime+timedelta(days=1)
        cp_year = cp_time.strftime('%Y')
        cp_month = cp_time.strftime('%m')
        cp_day = cp_time.strftime('%d')
        logging.info(f"copy file nas {cp_time}")
        output_folder_ftp_list=[f"{File.config_file['nas_path']}",'{}'.format(cp_time.strftime('%Y')),
                    '{}'.format(cp_time.strftime('%m'))]
        output_folder_ftp = os.path.join(*output_folder_ftp_list[:])
        exist_or_create_dir(output_folder_ftp)
        process_cp = subprocess.run(["cp", "-r", f"{File.config_file['output_path']}/{cp_year}/{cp_month}/{cp_day}/.",
                    f"{File.config_file['nas_path']}/{cp_year}/{cp_month}/{cp_day}/"])
        logging.info("end if copy files")

if __name__ == "__main__":
    ex_path = os.path.dirname(os.path.abspath(__file__))
    logging_config_init(ex_path)
    logging_start(ex_path)
    logging.info("server start eng")

    run_daily()

    # schedule.every().day.at("22:10").do(run_daily)

    # while True:
    #     # Checks whether a scheduled task
    #     # is pending to run or not
    #     schedule.run_pending()
    #     time.sleep(30)