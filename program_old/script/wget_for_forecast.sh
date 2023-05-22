#!/bin/bash
#Program:
#   download GEOS file using wget for forecast
# 2020/10/09
initdaysago=1
echo init $initdaysago daysago
read -t2 -p 'select day: ' dayago
if $dayago
then dayago=$initdaysago
    echo no input value
fi
echo $dayago daysago
# you can give data stroage path you want
# path=/data/GEOS5/
cd './../../'
path=$(pwd)'/'
echo "mypath: "$path
#!!!!!!!!!!select day!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
select='2020-09-23'                         #!!
echo $(date --date='2020-09-23 UTC')
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
year=$(date +'%Y');month=$(date +'%m');day=$(date +'%d')
echo $day2
year=$(date +'%Y' --date="-$dayago day")
month=$(date +'%m' --date="-$dayago day")
day=$(date +'%d' --date="-$dayago day")
echo $year,$month,$day
mkdir -p ./portal.nccs.nasa.gov/datashare/gmao/geos-fp/forecast/Y$year/M$month/D$day/H00
# python3 ./program/lib/get_data_fromftp_forecast.py $dayago


echo "Hi, I'm sleeping for 5 seconds..."
sleep 2
# filepath=portal.nccs.nasa.gov/datashare/gmao/geos-fp/forecast/Y$year/M$month/D$day/H00/downloadfile_forecast.txt
filepath=portal.nccs.nasa.gov/datashare/gmao/geos-fp/forecast/Y$year/M$month/D$day/H00/downloadfile_forecast_1.txt
echo $filepath
wget -x -bq -nv -i $path$filepath
sleep 1
filepath=portal.nccs.nasa.gov/datashare/gmao/geos-fp/forecast/Y$year/M$month/D$day/H00/downloadfile_forecast_2.txt
echo $filepath
wget -x -bq -nv -i $path$filepath
sleep 1
filepath=portal.nccs.nasa.gov/datashare/gmao/geos-fp/forecast/Y$year/M$month/D$day/H00/downloadfile_forecast_3.txt
echo $filepath
wget -x -bq -nv -i $path$filepath
sleep 1
filepath=portal.nccs.nasa.gov/datashare/gmao/geos-fp/forecast/Y$year/M$month/D$day/H00/downloadfile_forecast_4.txt
echo $filepath
wget -x -bq -nv -i $path$filepath
sleep 1
filepath=portal.nccs.nasa.gov/datashare/gmao/geos-fp/forecast/Y$year/M$month/D$day/H00/downloadfile_forecast_5.txt
echo $filepath
wget -x -bq -nv -i $path$filepath
sleep 1
filepath=portal.nccs.nasa.gov/datashare/gmao/geos-fp/forecast/Y$year/M$month/D$day/H00/downloadfile_forecast_6.txt
echo $filepath
wget -x -bq -nv -i $path$filepath
sleep 1
filepath=portal.nccs.nasa.gov/datashare/gmao/geos-fp/forecast/Y$year/M$month/D$day/H00/downloadfile_forecast_7.txt
echo $filepath
wget -x -bq -nv -i $path$filepath

#-b can select log file path
# cp -r ./output_forecast/2020/10/07/. /mnt/forecast/forecast_img/geos5/2020/10/07/
# cp -r ./output_forecast/2020/10/07/. /data/forecast_img/geos5/2020/10/07/