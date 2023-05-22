import os,time
import requests
from datetime import datetime,timedelta
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
                print(local_filename)
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
                    print(r.headers)
                    i += 1
                    print(f"download error size too small retry {i} times")
            else:
                time.sleep(3)
                print(r.headers)
                i += 1
                print(f"download error retry {i} times")
                if i > 5:
                    return None

def download_daily(day_list:list):
    file_path = "/downloads"
    for idate in day_list:
        threading_queue = []
        datetime_now = idate.replace(hour=0,minute=0,second=0,microsecond=0)
        styear = datetime_now
        etyear = datetime_now+timedelta(days=8)
        url = "https://portal.nccs.nasa.gov/cgi-lats4d/webform.cgi"
        request_file = f"?i=GEOS-5%2Ffp%2F0.25_deg%2Ffcast%2Finst1_2d_hwl_Nx%2Finst1_2d_hwl_Nx.{datetime_now:%Y%m%d}_00"
        vars = "&vars=totexttau&vars=ssexttau&vars=ocexttau&vars=suexttau&vars=bcexttau&vars=duexttau"
        datatimes = f"&year={styear.year}&month={styear:%b}&day={styear.day}&hour=0&yearend={etyear.year}&monthend={etyear:%b}&dayend={etyear.day}&hourend=0"
        parameter = "&ntimes=&tincr=6&levsbegin=1&levsend=1&levsinput=&selectedBaseLayer=&OpenLayers.Control.LayerSwitcher_26_baseLayers=OpenLayers+WMS"
        location = "&interactionType=box&NorthLatitude=40&WestLongitude=60&EastLongitude=150&SouthLatitude=0&West=&North=&East=&South=&area=&regridmask=&regridmethod=&format=coards&service=Download"
        request_url = url + request_file + vars + datatimes + parameter + location
        request_file_path = request_file.replace("%2F","/").replace("?i=","")
        print(f"download file path {request_file_path}")
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
        location = "&interactionType=box&NorthLatitude=40&WestLongitude=60&EastLongitude=150&SouthLatitude=0&West=&North=&East=&South=&area=&regridmask=&regridmethod=&format=coards&service=Download"
        request_url = url + request_file + vars + datatimes + parameter + location
        request_file_path = request_file.replace("%2F","/").replace("?i=","")
        print(f"download file path {request_file_path}")
        # start_download = datetime.now()
        threading_obj = threading.Thread(target=download_file, args=(request_url,file_path,datetime_now), daemon=True)
        threading_obj.start()
        threading_queue.append(threading_obj)
        # download_file(request_url,file_path,datetime_now)
        for i in threading_queue:
            i.join()
        print(f"download using time {datetime.now()-start_download}")

if __name__ == "__main__":
    day_list = [datetime.utcnow()-timedelta(days=1)]
    download_daily(day_list)