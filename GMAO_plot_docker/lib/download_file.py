import os,time,re
import requests
import logging
from datetime import datetime,timedelta
from lib.util import File,exist_or_create_dir
import threading

def download_file(url:str,file_path:str,request_date:datetime):
    if not os.path.isdir(os.path.join(file_path,f"{request_date:%Y}")):os.mkdir(os.path.join(file_path,f"{request_date:%Y}"))
    if not os.path.isdir(os.path.join(file_path,f"{request_date:%Y/%m}")):os.mkdir(os.path.join(file_path,f"{request_date:%Y/%m}"))
    i = 0
    while True:
        # NOTE the stream=True parameter below
        with requests.get(url, stream=True) as r:
            # r.raise_for_status()
            # print(r.headers)
            if r.headers["Content-Type"] == "application/force-download":
                local_filename = r.headers["Content-Disposition"].split('"')[1].split('-')[0]+'.nc'
                local_filename = os.path.join(file_path,f"{request_date:%Y}",f"{request_date:%m}",local_filename)
                logging.info(local_filename)
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192): 
                        # If you have chunk encoded response uncomment if
                        # and set chunk_size parameter to None.
                        #if chunk: 
                        f.write(chunk)
                if os.path.getsize(local_filename) > 20*1024*1024:
                    return local_filename
                else:
                    time.sleep(3)
                    logging.error(r.headers)
                    i += 1
                    logging.error(f"download error size too small retry {i} times")
            else:
                time.sleep(1)
                logging.info(r.headers)
                i += 1
                logging.error(f"download error retry {i} times")
                if i > 3:
                    return None

def download_daily(day_list:list):
    file_path = File.config_file["data_path"]
    for idate in day_list:
        threading_queue = []
        datetime_now = idate.replace(hour=0,minute=0,second=0,microsecond=0)

        datafolder = [f'{datetime_now:%Y}', f'{datetime_now:%m}']
        data_folder = os.path.join(File.config_file["data_path"],*datafolder[:])
        exist_or_create_dir(data_folder)
        # print(data_folder)
        files = os.listdir(data_folder)
        files_GEOS_inst1_2d_hwl_Nx = [f for f in files if re.match(r"inst1_2d_hwl_Nx.{init}.nc"\
                            .format(init=datetime_now.strftime("%Y%m%d_%H")),f)]
        files_GEOS_inst1_3d_asm_Np = [f for f in files if re.match(r"inst3_3d_asm_Np.{init}.nc"\
                                .format(init=datetime_now.strftime("%Y%m%d_%H")),f)]
        if len(files_GEOS_inst1_2d_hwl_Nx)==1 and len(files_GEOS_inst1_3d_asm_Np)==1:
            logging.info(f"file detected {files_GEOS_inst1_2d_hwl_Nx[0]}, {files_GEOS_inst1_3d_asm_Np[0]}")
            continue
        else:
            logging.info(f"request to download")

        styear = datetime_now
        etyear = datetime_now+timedelta(days=8)
        # etyear = datetime_now+timedelta(days=7)
        # https://portal.nccs.nasa.gov/cgi-lats4d/webform.cgi?i=GEOS-5%2Ffp%2F0.25_deg%2Ffcast%2Finst1_2d_hwl_Nx%2Finst1_2d_hwl_Nx.20221225_00
        # &vars=occmass&vars=coclbbae&vars=so2cmass&vars=so4smass&vars=nismass&vars=coclnbgl&vars=ocexttau
        # &year=2022&month=Dec&day=24&hour=22&yearend=2023&monthend=Jan&dayend=03&hourend=22&ntimes=&tincr=6
        # &levsbegin=1&levsend=1&levsinput=&selectedBaseLayer=&OpenLayers.Control.LayerSwitcher_26_baseLayers=OpenLayers+WMS
        # &interactionType=box&NorthLatitude=54.421870708466&WestLongitude=83.14453125&EastLongitude=153.45703125000003
        # &SouthLatitude=9.421870708465597&West=83.14453125&North=54.421870708466&East=153.45703125000003&South=9.421870708465597
        # &area=3164.06250000003&regridmask=&regridmethod=&format=coards&service=Download
        url = "https://portal.nccs.nasa.gov/cgi-lats4d/webform.cgi"
        request_file = f"?i=GEOS-5%2Ffp%2F0.25_deg%2Ffcast%2Finst1_2d_hwl_Nx%2Finst1_2d_hwl_Nx.{datetime_now:%Y%m%d}_00"
        vars = "&vars=totexttau&vars=ssexttau&vars=ocexttau&vars=suexttau&vars=bcexttau&vars=duexttau"
        datatimes = f"&year={styear.year}&month={styear:%b}&day={styear.day}&hour=0&yearend={etyear.year}&monthend={etyear:%b}&dayend={etyear.day}&hourend=0"
        parameter = "&ntimes=&tincr=6&levsbegin=1&levsend=1&levsinput=&selectedBaseLayer=&OpenLayers.Control.LayerSwitcher_26_baseLayers=OpenLayers+WMS"
        location = "&interactionType=box&NorthLatitude=40&WestLongitude=60&EastLongitude=150&SouthLatitude=0&West=64.9951171875&North=56.42578125&East=143.7451171875&South=12.83203125&area=3433.0078125&regridmask=&regridmethod=&format=coards&service=Download"
        request_url = url + request_file + vars + datatimes + parameter + location
        request_file_path = request_file.replace("%2F","/").replace("?i=","")
        print(request_url)
        logging.info(f"download file path {request_file_path}")
        start_download = datetime.now()
        threading_obj = threading.Thread(target=download_file, args=(request_url,file_path,datetime_now), daemon=True)
        threading_obj.start()
        threading_queue.append(threading_obj)
        # download_file(request_url,file_path,datetime_now)
        # print(f"download 2d Nx using time {datetime.now()-start_download}")

        url = "https://portal.nccs.nasa.gov/cgi-lats4d/webform.cgi"
        request_file = f"?i=GEOS-5%2Ffp%2F0.25_deg%2Ffcast%2Finst3_3d_asm_Np%2Finst3_3d_asm_Np.{datetime_now:%Y%m%d}_00"
        vars = "&vars=v&vars=u"
        datatimes = f"&year={styear.year}&month={styear:%b}&day={styear.day}&hour=0&minutes=0&yearend={etyear.year}&monthend={etyear:%b}&dayend={etyear.day}&hourend=0&minutesend=0"
        parameter = "&ntimes=&tincr=2&levsbegin=&levsend=&levsinput=1000%2C925%2C850%2C700%2C500&levsinput=&selectedBaseLayer=&OpenLayers.Control.LayerSwitcher_26_baseLayers=OpenLayers+WMS"
        location = "&interactionType=box&NorthLatitude=40&WestLongitude=60&EastLongitude=150&SouthLatitude=0&West=64.9951171875&North=56.42578125&East=143.7451171875&South=12.83203125&area=3433.0078125&regridmask=&regridmethod=&format=coards&service=Download"
        request_url = url + request_file + vars + datatimes + parameter + location
        request_file_path = request_file.replace("%2F","/").replace("?i=","")
        print(request_url)
        logging.info(f"download file path {request_file_path}")
        # start_download = datetime.now()
        threading_obj = threading.Thread(target=download_file, args=(request_url,file_path,datetime_now), daemon=True)
        threading_obj.start()
        threading_queue.append(threading_obj)
        # download_file(request_url,file_path,datetime_now)
        for i in threading_queue:
            i.join()
        logging.info(f"download using time {datetime.now()-start_download}")