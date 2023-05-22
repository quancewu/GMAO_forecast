import os,sys,re
import numpy as np
from datetime import datetime,timedelta
from info import sites_data
from util import append_value,exist_or_create_dir,datetime_range
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from matplotlib import colorbar
# from matplotlib import rcParams
# rcParams['font.family'] = 'Garuda'
# rcParams['font.sans-serif'] = "Garuda"
from cartopy import config
import cartopy.crs as ccrs
from cartopy.io.img_tiles import Stamen
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

from PIL import Image

def data_checker(data_folder,file_list):
    ex_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_folder = os.path.join(ex_dir,'log_file')
    exist_or_create_dir(log_file_folder)
    log_file_path = os.path.join(log_file_folder,'log.dat')
    flag = 1
    if file_list == []:
        with open(log_file_path, 'a+') as filehandle:
            filehandle.write("{}No souch file {}\n".format(datetime.now(),os.path.join(data_folder, f)))
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
                    filehandle.write("{}can't open file in path {}\n".format(datetime.now(),os.path.join(data_folder, f)))
                    filehandle.write("{} error {}\n".format(datetime.now(),e))

                flag = 1
                print('flag = {}'.format(flag))
    return flag
            


def plot_data(pressure_list,initdate,j_3hr,title_list,data_type_list):
    datafolder=['portal.nccs.nasa.gov','datashare','gmao','geos-fp','forecast','Y{}'.format(initdate.strftime('%Y')),
                'M{}'.format(initdate.strftime('%m')),'D{}'.format(initdate.strftime('%d')),
                'H{}'.format(initdate.strftime('%H'))]
    #============================================================================
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ex_dir = os.path.dirname(os.path.abspath(__file__))
    print(base_dir)
    print(*datafolder)
    data_folder = os.path.join(base_dir,*datafolder[:])
    fig_folder = os.path.join(ex_dir,'fig')
    exist_or_create_dir(data_folder)
    exist_or_create_dir(fig_folder)
    print(data_folder)
    files = os.listdir(data_folder)

    # for f in files:
    #     fullpath = os.path.join(data_folder, f)
    #     print(fullpath)  
    files_GEOS_inst1_2d_hwl_Nx = [f for f in files if re.match(r"GEOS.fp.fcst.inst1_2d_hwl_Nx.{init}\+{forecast}.V\d+.nc4"\
                            .format(init=initdate.strftime("%Y%m%d_%H"),forecast=j_3hr.strftime("%Y%m%d_%H%M")),f)]
    files_GEOS_inst1_3d_asm_Np = [f for f in files if re.match(r"GEOS.fp.fcst.inst3_3d_asm_Np.{init}\+{forecast}.V\d+.nc4"\
                            .format(init=initdate.strftime("%Y%m%d_%H"),forecast=j_3hr.strftime("%Y%m%d_%H%M")),f)]
        
    print(files_GEOS_inst1_2d_hwl_Nx,files_GEOS_inst1_3d_asm_Np)

    checker_1 = data_checker(data_folder,files_GEOS_inst1_2d_hwl_Nx)
    checker_2 = data_checker(data_folder,files_GEOS_inst1_3d_asm_Np)
    if (checker_1 + checker_2) > 0:
        print("data lost please read log file")
        return
    # data from _inst1_2d_hwl_Nx
    ncin = Dataset(os.path.join(data_folder, files_GEOS_inst1_2d_hwl_Nx[0]),'r',format='NCTCDF4')
    # print(ncin.file_format)
    # print(ncin.variables.keys())
    # # get dimensions
    # print(ncin.dimensions.keys())
    # print(ncin.dimensions['time'])
    # print(ncin.variables['TOTEXTTAU'].missing_value)
    totextau = np.array(ncin.variables['TOTEXTTAU'][0,:,:]) #total aerosol extinction aot [550 nm]
    totextau [totextau == ncin.variables['TOTEXTTAU'].missing_value] = np.nan
    duexttau = np.array(ncin.variables['DUEXTTAU'][0,:,:]) #dust column u-wind mass flux __ensemble__
    duexttau [duexttau == ncin.variables['DUEXTTAU'].missing_value] = np.nan
    ocexttau = np.array(ncin.variables['OCEXTTAU'][0,:,:]) #organic carbon extinction aot [550 nm] __ensemble__
    ocexttau [ocexttau == ncin.variables['OCEXTTAU'].missing_value] = np.nan
    bcexttau = np.array(ncin.variables['BCEXTTAU'][0,:,:]) #black carbon extinction aot [550 nm] __ensemble__
    bcexttau [bcexttau == ncin.variables['BCEXTTAU'].missing_value] = np.nan
    suexttau = np.array(ncin.variables['SUEXTTAU'][0,:,:]) #so4 extinction aot [550 nm] __ensemble__
    suexttau [suexttau == ncin.variables['SUEXTTAU'].missing_value] = np.nan

    # smoke = black carbon + organic carbon
    # print(totextau.shape)
    smexttau = bcexttau + ocexttau

    #data from_GEOS_inst1_3d_asm_Np
    ncin = Dataset(os.path.join(data_folder, files_GEOS_inst1_3d_asm_Np[0]),'r',format='NCTCDF4')
    # print(ncin.file_format)
    # print(ncin.variables.keys())

    U_500 = np.array(ncin.variables['U'][0,21,:,:])
    U_500 [U_500 == ncin.variables['U'].missing_value] = np.nan
    V_500 = np.array(ncin.variables['V'][0,21,:,:])
    V_500 [V_500 == ncin.variables['V'].missing_value] = np.nan

    U_700 = np.array(ncin.variables['U'][0,13,:,:])
    U_700 [U_700 == ncin.variables['U'].missing_value] = np.nan
    V_700 = np.array(ncin.variables['V'][0,13,:,:])
    V_700 [V_700 == ncin.variables['V'].missing_value] = np.nan
    
    U_850 = np.array(ncin.variables['U'][0,5,:,:])
    U_850 [U_850 == ncin.variables['U'].missing_value] = np.nan
    V_850 = np.array(ncin.variables['V'][0,5,:,:]) 
    V_850 [V_850 == ncin.variables['V'].missing_value] = np.nan

    U_925 = np.array(ncin.variables['U'][0,2,:,:])
    U_925 [U_925 == ncin.variables['U'].missing_value] = np.nan
    V_925 = np.array(ncin.variables['V'][0,2,:,:]) 
    V_925 [V_925 == ncin.variables['V'].missing_value] = np.nan

    U_1000 = np.array(ncin.variables['U'][0,0,:,:])
    U_1000 [U_1000 == ncin.variables['U'].missing_value] = np.nan
    V_1000 = np.array(ncin.variables['V'][0,0,:,:]) 
    V_1000 [V_1000 == ncin.variables['V'].missing_value] = np.nan

    # get axis data
    # time = ncin.variables['time']
    latitude = ncin.variables['lat']
    longitude = ncin.variables['lon']
    lon,lat = np.meshgrid(longitude[:],latitude[:])
    for source in data_type_list:
        if source == 'TotalAOD':
            source_name = 'TotalAOD'
            data_source = totextau
        elif source == 'Smoke':
            source_name = 'Smoke'
            data_source = smexttau
        elif source == 'Dust':
            source_name = 'Dust'
            data_source = duexttau
        for level, title in zip(pressure_list,title_list):
            if level == 1000:
                U_data = U_1000
                V_data = V_1000
            elif level == 500:
                U_data = U_500
                V_data = V_500
            elif level == 700:
                U_data = U_700
                V_data = V_700
            elif level == 850:
                U_data = U_850
                V_data = V_850
            elif level == 925:
                U_data = U_925
                V_data = V_925
            initdate_LST = initdate + timedelta(hours=8)
            forecasttime_LST = j_3hr + timedelta(hours=8)
            initdate_str = initdate_LST.strftime('%Y%m%d %H UTC+8')
            forecastdate_str = forecasttime_LST.strftime('%Y%m%d %H UTC+8')
            # print('initial time = ',initdate_str,'forecast time',forecastdate_str,'   data = ',source_name)
            fig,(axs) = plt.subplots(1,1,figsize=(14,8),subplot_kw={'projection': ccrs.PlateCarree()})
            plt.suptitle('GEOS-5 AOD forecast with {} wind'.format(title),
                                fontsize=22,fontweight='bold')
            interv = 8
            # colors = ["#f8fffe","#cefbef","#84f6e7","#63fa64","#fff600","#fe2009"]
            colors = ["#e7fcf9","#cefbef","#84f6e7","#63fa64","#fff600","#fe2009"]

            cmap= matplotlib.colors.LinearSegmentedColormap.from_list('',colors)
            cmap.set_over('red')
            # cmap.set_under('0.0')
            # nodes = [0.0, 0.2, 0.6, 0.8, 1.0, 1.2]
            nodes = [0.0, 0.23, 0.35, 0.54, 0.78, 1.0]

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

            im = axs.pcolormesh(lon,lat,data_source,cmap=cmap,norm=norm)
            ax.quiver(lon[::interv,::interv], lat[::interv,::interv],
                U_data[::interv,::interv], V_data[::interv,::interv],
                scale=8,scale_units='xy',
                headwidth=5,headlength=6,headaxislength=5,
                minshaft=3,color='k')
            cax1 = fig.add_axes([0.91, 0.08, 0.02, 0.82])
            # bounds = [0.,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
            bounds = [0.,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2]

            cb2 = plt.colorbar(im,cax=cax1,ticks=bounds)

            plt.subplots_adjust(left = 0.055,  # the left side of the subplots of the figure
                    right = 0.9,   # the right side of the subplots of the figure
                    bottom = 0.08,  # the bottom of the subplots of the figure
                    top = 0.895,     # the top of the subplots of the figure
                    wspace = 0.13,   # the amount of width reserved for space between subplots,
                                    # expressed as a fraction of the average axis width
                    hspace = 0.16)   # the amount of height reserved for space between subplots,
                                    # expressed as a fraction of the average axis height
            # plt.show()
            storage_day = initdate + timedelta(days=1)
            output_fig_folder_list=['output_forecast','{}'.format(storage_day.strftime('%Y')),
                    '{}'.format(storage_day.strftime('%m')),'{}'.format(storage_day.strftime('%d')),
                    str(source_name),'{}hpa'.format(str(level))]
            output_fig_folder = os.path.join(base_dir,*output_fig_folder_list[:])
            exist_or_create_dir(output_fig_folder)
            savename = os.path.join(output_fig_folder,'{}{}.png'.format(str(source_name),forecasttime_LST.strftime('%Y%m%d%H')))
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
    #============================================================================
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ex_dir = os.path.dirname(os.path.abspath(__file__))
    print(base_dir)
    print(*datafolder)
    data_folder = os.path.join(base_dir,*datafolder[:])
    fig_folder = os.path.join(ex_dir,'fig')
    exist_or_create_dir(data_folder)
    exist_or_create_dir(fig_folder)
    # print(data_folder)
    files = os.listdir(data_folder)
    starttime = datetime(2020,9,14)
    endtime = datetime(2020,9,17)
    starttime = initdate+timedelta(days=1)
    endtime = initdate+timedelta(days=forecast_range+1)
    forecast_list = np.array([dt for dt in datetime_range(starttime, endtime, {'hours': 6})])
    files_GEOS_inst1_2d_hwl_Nx=[]
    for idata in forecast_list:
        file_GEOS_inst1_2d_hwl_Nx = [f for f in files if re.match(r"GEOS.fp.fcst.inst1_2d_hwl_Nx.{init}\+{forecast}.V\d+.nc4"\
                                .format(init=initdate.strftime("%Y%m%d_%H"),forecast=idata.strftime("%Y%m%d_%H%M")),f)]
            
        print(file_GEOS_inst1_2d_hwl_Nx)

        checker_1 = data_checker(data_folder,file_GEOS_inst1_2d_hwl_Nx)
        if (checker_1) > 0:
            print("data lost please read log file")
            files_GEOS_inst1_2d_hwl_Nx.append(False)
        else:
            files_GEOS_inst1_2d_hwl_Nx.append(file_GEOS_inst1_2d_hwl_Nx[0])
    # storage_data = np.zeros((8,3,0))
    storage_data = dict()
    for iforecast in files_GEOS_inst1_2d_hwl_Nx:
        if iforecast == False:
            totextau = np.full((721,1152),np.nan)
            duexttau = np.full((721,1152),np.nan)
            smexttau = np.full((721,1152),np.nan)
        else:
            ncin = Dataset(os.path.join(data_folder, iforecast),'r',format='NCTCDF4')
            totextau = np.array(ncin.variables['TOTEXTTAU'][0,:,:]) #total aerosol extinction aot [550 nm]
            totextau [totextau == ncin.variables['TOTEXTTAU'].missing_value] = np.nan
            duexttau = np.array(ncin.variables['DUEXTTAU'][0,:,:]) #dust column u-wind mass flux __ensemble__
            duexttau [duexttau == ncin.variables['DUEXTTAU'].missing_value] = np.nan
            ocexttau = np.array(ncin.variables['OCEXTTAU'][0,:,:]) #organic carbon extinction aot [550 nm] __ensemble__
            ocexttau [ocexttau == ncin.variables['OCEXTTAU'].missing_value] = np.nan
            bcexttau = np.array(ncin.variables['BCEXTTAU'][0,:,:]) #black carbon extinction aot [550 nm] __ensemble__
            bcexttau [bcexttau == ncin.variables['BCEXTTAU'].missing_value] = np.nan
            suexttau = np.array(ncin.variables['SUEXTTAU'][0,:,:]) #so4 extinction aot [550 nm] __ensemble__
            suexttau [suexttau == ncin.variables['SUEXTTAU'].missing_value] = np.nan

            # smoke = black carbon + organic carbon
            # print(totextau.shape)
            smexttau = bcexttau + ocexttau
        
        for i,site in enumerate(sites):
            # print(i,site)
            # print(sites_data.information[site]['lat'],sites_data.information[site]['lon'])
            latinarray = int( ( - sites_data.information[site]['lat'] + 90 ) / 0.25 ) 
            loninarray = int( ( sites_data.information[site]['lon'] + 180 ) / 0.312 ) 
            dummy = {site:[totextau[latinarray,loninarray],duexttau[latinarray,loninarray],smexttau[latinarray,loninarray]]}
            append_value(storage_data,site,dummy[site])

    for i,site in enumerate(sites):
        print(i,site)
        color = ['#234990','#EC3D33','#c98708'] #F5B12E
        data = np.array(storage_data[site])
        Pollutants = np.transpose(data)
        # print(Pollutants[1,:],Pollutants[1,:].shape)
        fig,ax1 = plt.subplots(1,1,figsize=(16,9))
        ax1.plot(forecast_list,Pollutants[0,:],label = 'Total AOD',color = color[0],marker = 'o',alpha=0.8,lw=2)
        ax1.plot(forecast_list,Pollutants[2,:],label = 'Smoke',color = color[1],marker = 'o',alpha=0.8,lw=2)
        ax2 = ax1.twinx()
        ax2.plot(forecast_list,Pollutants[1,:],label = 'Dust',color = color[2],marker = 'o',alpha=0.8,lw=2)
        ax1.set_ylim([0, max(Pollutants[0,:]) + min(Pollutants[0,:])])
        ax2.set_ylim([0, max(Pollutants[1,:]) + min(Pollutants[1,:])])
        ax1.set_xlim([forecast_list[0]-timedelta(hours=6),forecast_list[-1]+timedelta(hours=6)])
        for axis in ['top','bottom','left','right']:
            ax1.spines[axis].set_linewidth(2)
            ax2.spines[axis].set_linewidth(2)
        ax1.set_ylabel('TotalAOD & Smoke',color=color[0],fontsize=16)
        ax2.set_ylabel('Dust',color=color[2],fontsize=16)
        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        formatter.formats = ['%y',  # ticks are mostly years
                            '%b',       # ticks are mostly months
                            '%b-%d',       # ticks are mostly days
                            '%H',    # hrs
                            '%H:%M',    # min
                            '%S.%f', ]  # secs
        # these are mostly just the level above...
        formatter.zero_formats = [''] + formatter.formats[:-1]
        # ...except for ticks that are mostly hours, then it is nice to have
        # month-day:
        # print(formatter.zero_formats)

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
        plt.suptitle('GEOS-5 TotalAOD, Smoke and Dust forecast in {}'.format(site),
                                fontsize=22,fontweight='bold')
        initdate_str = initdate.strftime('%Y%m%d %H UTC')
        ax1.set_title('   Initial at {}'.format(initdate_str),fontsize=18)
        # plt.show()
        storage_day = initdate + timedelta(days=1)
        output_fig_folder_list=['output_forecast','{}'.format(storage_day.strftime('%Y')),
                '{}'.format(storage_day.strftime('%m')),'{}'.format(storage_day.strftime('%d')),
                'Graph']
        output_fig_folder = os.path.join(base_dir,*output_fig_folder_list[:])
        exist_or_create_dir(output_fig_folder)
        plt.subplots_adjust(left = 0.1,  # the left side of the subplots of the figure
                    right = 0.9,   # the right side of the subplots of the figure
                    bottom = 0.10,  # the bottom of the subplots of the figure
                    top = 0.895,     # the top of the subplots of the figure
                    wspace = 0.13,   # the amount of width reserved for space between subplots,
                                    # expressed as a fraction of the average axis width
                    hspace = 0.16)   # the amount of height reserved for space between subplots,
                                    # expressed as a fraction of the average axis height
        savename = os.path.join(output_fig_folder,'{}.png'.format(site.replace(' ','_').replace('.','_')))
        fig.savefig(savename,dpi = 300)
        output_data_folder_list=['output_forecast','{}'.format(storage_day.strftime('%Y')),
                '{}'.format(storage_day.strftime('%m')),'{}'.format(storage_day.strftime('%d')),'data']
        output_data_folder = os.path.join(base_dir,*output_data_folder_list[:])
        exist_or_create_dir(output_data_folder)
        datasavename = os.path.join(output_data_folder,'{}.csv'.format(site.replace(' ','_').replace('.','_')))
        storagearry = np.vstack((forecast_list,Pollutants))
        time_headr = 'time,Total_AOD,Dust,Smoke'
        np.savetxt(datasavename,storagearry.T,fmt='%s,%5.4f,%5.4f,%5.4f',delimiter=',',
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
    # test
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
    DataTime = datetime.strptime("2020-09-23 0000", "%Y-%m-%d %H%M")
    forecasttime = datetime.strptime("2020-09-23 0600", "%Y-%m-%d %H%M")
    Pressure=[1000,925,850,700,500]
    title=['1000hPa','925hPa','850hPa','700hPa','500hPa']
    # sulfate SUEXTTAU sea salt SSCMASS sscmass
    data_type=['TotalAOD','Smoke','Dust']
    Sites = ["NCU","Mt.Lulin","Dongsha","Tai Ping","Son La","Doi Ang Khang","Chiang Mai","Bangkok"]
    plot_data(pressure_list = Pressure,initdate=DataTime,j_3hr=forecasttime,title_list=title,data_type_list=data_type)
    serial_data_plot_storage(initdate=DataTime,forecast_range=7,data_type_list=data_type,sites=Sites)