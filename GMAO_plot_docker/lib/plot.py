import os,sys,re
import numpy as np
os.environ['MPLCONFIGDIR'] = "/home/project/gmao"
from datetime import datetime,timedelta
import logging
from lib.util import File
import json 
from lib.util import sites_data
from lib.util import append_value,exist_or_create_dir,datetime_range
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from matplotlib import colorbar
from cartopy import config as carconfig
carconfig['data_dir'] = "/home/project/gmao/.local"
import cartopy.crs as ccrs
from cartopy.io.img_tiles import Stamen
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

from PIL import Image

def data_checker(data_folder,file_list):
    base_ex_dir =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_file_folder = os.path.join(base_ex_dir,'log_file')
    exist_or_create_dir(log_file_folder)
    log_file_path = os.path.join(log_file_folder,'log.dat')
    flag = 1
    if file_list == []:
        with open(log_file_path, 'a+') as filehandle:
            filehandle.write("{} No souch file \n".format(datetime.now()))
            flag = 1
            print('flag = {}'.format(flag))
    else:
        for f in file_list:
            try:
                # print(os.path.join(data_folder, f))
                ncin = Dataset(os.path.join(data_folder, f),'r',format='NCTCDF4')
                flag = 0
            except Exception as e:
                with open(log_file_path, 'a+') as filehandle:
                    filehandle.write("{} can't open file in path {}\n".format(datetime.now(),os.path.join(data_folder, f)))
                    filehandle.write("{} error {}\n".format(datetime.now(),e))

                flag = 1
                print('flag = {}'.format(flag))
    return flag

def nc4_reader(ncfile,data_nmae):
    data_nmae = [a.lower() for a in data_nmae]
    for i,idata in enumerate(data_nmae):
        if i != 0:
            dummy = np.array(ncfile.variables[idata])
            dummy [dummy == ncfile.variables[idata].missing_value] = np.nan
            data = data + dummy
        else:    
            data = np.array(ncfile.variables[idata])
            data [data == ncfile.variables[idata].missing_value] = np.nan
    return data

def plot_data(pressure_list,initdate,foreacst_date,title_list,data_type_list):
    datafolder=['portal.nccs.nasa.gov','datashare','gmao','geos-fp','forecast','Y{}'.format(initdate.strftime('%Y')),
                'M{}'.format(initdate.strftime('%m')),'D{}'.format(initdate.strftime('%d')),
                'H{}'.format(initdate.strftime('%H'))]
    datafolder = [f'{initdate:%Y}', f'{initdate:%m}']
    #============================================================================
    # base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ex_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # data_folder = os.path.join("/mnt/228sftp/upload/GEOS5",*datafolder[:])
    data_folder = os.path.join(File.config_file["data_path"],*datafolder[:])
    exist_or_create_dir(data_folder)
    # print(data_folder)
    files = os.listdir(data_folder)
    #============================================================================
    filename = os.path.join(ex_dir,'config','config.json')
    with open(filename) as json_file: 
        data_info = json.load(json_file)
    # print(data_info['Source']) 
    # print(files)
    files_GEOS_inst1_2d_hwl_Nx = [f for f in files if re.match(r"inst1_2d_hwl_Nx.{init}.nc"\
                            .format(init=initdate.strftime("%Y%m%d_%H")),f)]
    files_GEOS_inst1_3d_asm_Np = [f for f in files if re.match(r"inst3_3d_asm_Np.{init}.nc"\
                            .format(init=initdate.strftime("%Y%m%d_%H")),f)]
      
    logging.info(f"detect file {files_GEOS_inst1_2d_hwl_Nx}, {files_GEOS_inst1_3d_asm_Np}")

    checker_1 = data_checker(data_folder,files_GEOS_inst1_2d_hwl_Nx)
    checker_2 = data_checker(data_folder,files_GEOS_inst1_3d_asm_Np)
    if (checker_1 + checker_2) > 0:
        logging.info("data lost please read log file")
        return "can't plot this time"
    # data from _inst1_2d_hwl_Nx
    ncin = Dataset(os.path.join(data_folder, files_GEOS_inst1_2d_hwl_Nx[0]),'r',format='NCTCDF4')
    data_dict = dict()
    for data_type in data_type_list:
        data_dict.update({data_type: nc4_reader(ncin,data_info['Source'][data_type])[:,:,:]})
    test = ncin
    #data from_GEOS_inst1_3d_asm_Np
    ncin = Dataset(os.path.join(data_folder, files_GEOS_inst1_3d_asm_Np[0]),'r',format='NCTCDF4')

    data_dict.update({'U': nc4_reader(ncin,'U')[:,:,:,:]})
    data_dict.update({'V': nc4_reader(ncin,'V')[:,:,:,:]})
    # get axis data
    latitude = ncin.variables['latitude']
    longitude = ncin.variables['longitude']
    lon,lat = np.meshgrid(longitude[:],latitude[:])
    level_dict = {
        "1000": 0,
        "925": 1,
        "850": 2,
        "700": 3,
        "500": 4
    }
    init_time = datetime.strptime(ncin.variables["time"].units,"hours since %Y-%m-%d %H") 
    time_delta = ncin.variables['time'][:]
    time_list = []
    forecast_time_dict = dict()
    for i,itime in enumerate(time_delta):
        time_list.append(init_time+timedelta(hours=itime))
        forecast_time_dict.update({f'{init_time+timedelta(hours=itime)}':i})
    for foreacst_datetime in time_list:
        for data_type in data_type_list:
            source_name = data_type.replace(' ','_')
            forecast_id = forecast_time_dict[f"{foreacst_datetime}"]
            data_source = data_dict[data_type][forecast_id,:,:]
            logging.info(f"forecast_id: {forecast_id}")
            for Pressure, title in zip(pressure_list,title_list):
                level = round( ( 1000 - Pressure ) / 24.387804 )
                level = level_dict[f"{Pressure}"]
                U_data = data_dict['U'][forecast_id,level,:,:]
                V_data = data_dict['V'][forecast_id,level,:,:]
                initdate_LST = initdate + timedelta(hours=8)
                forecasttime_LST = foreacst_datetime + timedelta(hours=8)
                initdate_str = initdate_LST.strftime('%Y%m%d %H UTC+8')
                forecastdate_str = forecasttime_LST.strftime('%Y%m%d %H UTC+8')
                fig,(axs) = plt.subplots(1,1,figsize=(14,8),subplot_kw={'projection': ccrs.PlateCarree()})
                plt.suptitle('GEOS-5 {} forecast with {} wind'.format(data_type,title),
                                    fontsize=22,fontweight='bold')
                interv = 8
                colors = ["#ffffff","#ffffff","#84f6e7","#63fa64","#fffc3f","#ffe000","#fe2009"]
                nodes =  [0.0, 0.14, 0.21, 0.5, 0.7, 0.82, 1.0]
                cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", list(zip(nodes, colors)))
                ax = axs
                ax.set_title('   Initial at {}   Valid at {}'.format(initdate_str,forecastdate_str),fontsize=18)
                extent = [70, 140, 0, 40]
                ax.set_extent(extent)
                ax.set_xticks(np.linspace(extent[0],extent[1],8),crs=ccrs.PlateCarree()) # set longitude indicators
                ax.set_yticks(np.linspace(extent[2],extent[3],5),crs=ccrs.PlateCarree()) # set latitude indicators
                lon_formatter = LongitudeFormatter(number_format='0.1f',degree_symbol='',dateline_direction_label=True) # format lons
                lat_formatter = LatitudeFormatter(number_format='0.1f',degree_symbol='') # format lats
                ax.xaxis.set_major_formatter(lon_formatter) # set lons
                ax.yaxis.set_major_formatter(lat_formatter) # set lats
                ax.xaxis.set_tick_params(labelsize=14)
                ax.yaxis.set_tick_params(labelsize=14)
                ax.set_ylim([extent[2],extent[3]])
                ax.coastlines('10m')

                norm= matplotlib.colors.Normalize(vmin=0,vmax=1.2)

                im = axs.pcolormesh(lon,lat,data_source,cmap=cmap,norm=norm,shading='auto')
                ax.quiver(lon[::interv,::interv], lat[::interv,::interv],
                    U_data[::interv,::interv], V_data[::interv,::interv],
                    scale=8,scale_units='xy',
                    headwidth=5,headlength=6,headaxislength=5,
                    minshaft=3,color='k')
                cax1 = fig.add_axes([0.91, 0.08, 0.02, 0.82])
                bounds = [0.,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2]

                cb2 = plt.colorbar(im,cax=cax1,ticks=bounds)

                plt.subplots_adjust(left = 0.055,       # the left side of the subplots of the figure
                                    right = 0.9,        # the right side of the subplots of the figure
                                    bottom = 0.08,      # the bottom of the subplots of the figure
                                    top = 0.895,        # the top of the subplots of the figure
                                    wspace = 0.13,      # the amount of width reserved for space between subplots,
                                                        # expressed as a fraction of the average axis width
                                    hspace = 0.16)      # the amount of height reserved for space between subplots,
                                                        # expressed as a fraction of the average axis height
                # plt.show()
                storage_day = initdate + timedelta(days=1)
                output_fig_folder_list=['{}'.format(storage_day.strftime('%Y')),
                        '{}'.format(storage_day.strftime('%m')),'{}'.format(storage_day.strftime('%d')),
                        str(source_name),'{}'.format(title)]
                output_fig_folder = os.path.join(File.config_file['output_path'],*output_fig_folder_list[:])
                exist_or_create_dir(output_fig_folder)
                savename = os.path.join(output_fig_folder,'{}{}.png'.format(str(source_name),forecasttime_LST.strftime('%Y%m%d%H')))
                # print(savename)
                fig.savefig(savename,dpi = 300)
                # Convert to 8 bit
                # Load image
                img = Image.open(savename)                                                                 
                # Convert to palette mode and save
                img.convert('P').save(savename)
                plt.clf()
                plt.close()

def serial_data_plot_storage(initdate,forecast_range,data_type_list,sites):
    plt.rcParams.update({'font.size': 16})
    datafolder=['portal.nccs.nasa.gov','datashare','gmao','geos-fp','forecast','Y{}'.format(initdate.strftime('%Y')),
                'M{}'.format(initdate.strftime('%m')),'D{}'.format(initdate.strftime('%d')),
                'H{}'.format(initdate.strftime('%H'))]
    datafolder = [f'{initdate:%Y}', f'{initdate:%m}']
    #============================================================================
    # base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ex_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_folder = os.path.join(File.config_file["data_path"],*datafolder[:])
    exist_or_create_dir(data_folder)
    files = os.listdir(data_folder)

    filename = os.path.join(ex_dir,'config','config.json')
    with open(filename) as json_file: 
        data_info = json.load(json_file)

    starttime = datetime(2020,9,14)
    endtime = datetime(2020,9,17)
    starttime = initdate+timedelta(days=1)
    endtime = initdate+timedelta(days=forecast_range+1)
    print(files)
    forecast_list = np.array([dt for dt in datetime_range(starttime, endtime, {'hours': 6})])
    file_GEOS_inst1_2d_hwl_Nx = [f for f in files if re.match(r"inst1_2d_hwl_Nx.{init}.nc"\
                            .format(init=initdate.strftime("%Y%m%d_%H")),f)]
    if len(file_GEOS_inst1_2d_hwl_Nx) == 0: 
        logging.info("ERROR no file")
        return None
    storage_data = dict()
    data_dict = dict()
    ncin = Dataset(os.path.join(data_folder, file_GEOS_inst1_2d_hwl_Nx[0]),'r',format='NCTCDF4')
    for data_type in data_type_list:
        data_dict.update({data_type: nc4_reader(ncin,data_info['Source'][data_type])[:,:,:]})
    # latitude = ncin.variables['latitude']
    # longitude = ncin.variables['longitude']
    for i,site in enumerate(sites):
        logging.info(f"{i}, {site}")
        # logging.info(f"{sites_data.information[site]['lat']}, {sites_data.information[site]['lon']}")
        latinarray = round( (sites_data.information[site]['lat']) / 0.25 ) 
        loninarray = round( ( sites_data.information[site]['lon'] - 60 ) / 0.312 ) 
        # data_dict["Total AOD"][4:32,latinarray,loninarray]
        temp = dict()
        for data_type in data_type_list: 
            temp.update({data_type: data_dict[data_type][4:4+len(forecast_list),latinarray,loninarray]})
        storage_data.update({site:temp})

    for i,site in enumerate(sites):
        # print(i,site)
        color = ['#234990','#E64B10','#c98708','#C82033','#45CBF3'] #F5B12E
        data = storage_data[site]
        # Pollutants = np.transpose(data)Total_AOD,Dust,Smoke,Sufate,Sea_salt
        Pollutants = np.vstack((data['Total AOD'],data['Dust'],data['Smoke'],data['Sulfate'],data['Sea salt']))
        fig,ax1 = plt.subplots(1,1,figsize=(16,9))
        ax1.plot(forecast_list,data["Total AOD"],label = 'Total AOD',color = color[0],marker = 'o',alpha=0.8,lw=2)
        ax1.plot(forecast_list,data["Smoke"],label = 'Smoke',color = color[1],marker = 'o',alpha=0.8,lw=2)
        ax1.plot(forecast_list,data["Sulfate"],label = 'Sulfate',color = color[3],marker = 'o',alpha=0.8,lw=2)
        ax1.plot(forecast_list,data["Sea salt"],label = 'Sea salt',color = color[4],marker = 'o',alpha=0.8,lw=2)
        ax2 = ax1.twinx()
        ax2.plot(forecast_list,data['Dust'],label = 'Dust',color = color[2],marker = 'o',alpha=0.8,lw=2)
        ax1.set_ylim([0, max(data["Total AOD"]) + min(data["Total AOD"])])
        ax2.set_ylim([0, max(data['Dust']) + min(data['Dust'])])
        ax1.set_xlim([forecast_list[0]-timedelta(hours=6),forecast_list[-1]+timedelta(hours=6)])
        for axis in ['top','bottom','left','right']:
            ax1.spines[axis].set_linewidth(2)
            ax2.spines[axis].set_linewidth(2)
        ax1.set_ylabel('TotalAOD & Smoke & Sulfate & Sea salt',color=color[0],fontsize=16)
        ax2.set_ylabel('Dust',color=color[2],fontsize=16)
        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        formatter.formats = ['%y',          # ticks are mostly years
                            '%b',           # ticks are mostly months
                            '%b-%d',        # ticks are mostly days
                            '%H',           # hrs
                            '%H:%M',        # min
                            '%S.%f', ]      # secs
        # these are mostly just the level above...
        formatter.zero_formats = [''] + formatter.formats[:-1]
        
        formatter.offset_formats = ['',
                                    '%Y',
                                    '%b %Y',
                                    '%d %b %Y',
                                    '%d %b %Y',
                                    '%d %b %Y %H:%M', ]
        formatter.offset_formats[3] = '%Y'
        ax1.xaxis.set_major_locator(locator)
        ax1.xaxis.set_major_formatter(formatter)
        ax1.xaxis.set_minor_formatter(formatter)
        ax1.xaxis.set_minor_locator(mdates.HourLocator(interval=6))
        ax1.tick_params(which='major', length=14, color='k', width=3, pad = 10, labelsize = 16)
        ax1.tick_params(which='minor', length=5, color='r', width=2, labelsize = 14)
        ax1.tick_params(axis = 'y',direction='out', length=6, width=2, colors=color[0],
                        grid_color='r', grid_alpha=0.5,labelsize = 16)
        ax2.tick_params(direction='out', length=6, width=2, colors=color[2],
                        grid_color='r', grid_alpha=0.5,labelsize = 16)
        for label in ax2.get_yticklabels():
            label.set_rotation(40)
            label.set_horizontalalignment('left')
            label.set_verticalalignment('center')
            label.set_rotation_mode('anchor')
        ax1.legend(loc='upper left',shadow=True, handlelength=1.5, fontsize=16)
        ax2.legend(loc='upper right',shadow=True, handlelength=1.5, fontsize=16)
        plt.suptitle('GEOS-5 forecast in {}'.format(site),
                                fontsize=22,fontweight='bold')
        initdate_str = initdate.strftime('%Y%m%d %H UTC')
        ax1.set_title('   Initial at {}'.format(initdate_str),fontsize=18)
        # plt.show()
        storage_day = initdate + timedelta(days=1)
        output_fig_folder_list=['{}'.format(storage_day.strftime('%Y')),
                '{}'.format(storage_day.strftime('%m')),'{}'.format(storage_day.strftime('%d')),
                'Graph']
        output_fig_folder = os.path.join(File.config_file['output_path'],*output_fig_folder_list[:])
        exist_or_create_dir(output_fig_folder)
        plt.subplots_adjust(left = 0.1,     # the left side of the subplots of the figure
                            right = 0.9,    # the right side of the subplots of the figure
                            bottom = 0.10,  # the bottom of the subplots of the figure
                            top = 0.895,    # the top of the subplots of the figure
                            wspace = 0.13,  # the amount of width reserved for space between subplots,
                                            # expressed as a fraction of the average axis width
                            hspace = 0.16)  # the amount of height reserved for space between subplots,
                                            # expressed as a fraction of the average axis height
        savename = os.path.join(output_fig_folder,'{}.png'.format(site.replace(' ','_').replace('.','_')))
        fig.savefig(savename,dpi = 300)
        output_data_folder_list=['{}'.format(storage_day.strftime('%Y')),
                '{}'.format(storage_day.strftime('%m')),'{}'.format(storage_day.strftime('%d')),'data']
        output_data_folder = os.path.join(File.config_file['output_path'],*output_data_folder_list[:])
        exist_or_create_dir(output_data_folder)
        datasavename = os.path.join(output_data_folder,'{}.csv'.format(site.replace(' ','_').replace('.','_')))
        storagearry = np.vstack((forecast_list,Pollutants))
        time_headr = 'time,Total_AOD,Dust,Smoke,Sulfate,Sea_salt'
        np.savetxt(datasavename,storagearry.T,fmt='%s,%5.4f,%5.4f,%5.4f,%5.4f,%5.4f',delimiter=',',
                 newline='\n', header=time_headr, footer='', comments='init time {} {}\n'.format(initdate_str,site),
                 encoding=None)
        # Convert to 8 bit
        # Load image
        img = Image.open(savename)                                                                 
        # Convert to palette mode and save
        img.convert('P').save(savename)
        plt.clf()
        plt.close()

        

if __name__ == "__main__":
    # run for testing
    # myString=''
    # while len(myString) < 1 : 
    #     print("datetime format YYYY-MM-DD 0000")
    #     myString = input("Enter search keywords: ")
    #     if len(myString) < 1:
    #         Datetime = datetime.now()
    #     else :
    #         DataTime = datetime.strptime(myString, "%Y-%m-%d %H%M")
    # print(DataTime)
    # datetime what you want
    DataTime = datetime.strptime("2022-11-22 0000", "%Y-%m-%d %H%M")
    forecasttime = datetime.strptime("2022-11-23 0600", "%Y-%m-%d %H%M")
    Pressure=[1000,925,850,700,500]
    title=['1000hPa','925hPa','850hPa','700hPa','500hPa']
    # sulfate SUEXTTAU sea salt SSCMASS sscmass
    data_type=['Total AOD','Smoke','Dust','Sulfate','Sea salt']
    Sites = ["NCU","Mt.Lulin","Dongsha","Tai Ping","Son La","Doi Ang Khang","Chiang Mai","Bangkok"]
    plot_data(pressure_list=Pressure,initdate=DataTime,foreacst_date=forecasttime,title_list=title,data_type_list=data_type)
    # serial_data_plot_storage(initdate=DataTime,forecast_range=7,data_type_list=data_type,sites=Sites)