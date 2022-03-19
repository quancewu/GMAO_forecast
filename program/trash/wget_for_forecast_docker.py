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
path=/GEOS5/
cd $path
python3 ./program/get_data_fromftp_forecast.py $dayago
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

echo "Hi, I'm sleeping for 5 seconds..."
sleep 5
filepath=portal.nccs.nasa.gov/datashare/gmao/geos-fp/forecast/Y$year/M$month/D$day/H00/downloadfile_forecast.txt
echo $filepath
wget -x -bq -nv -i $path$filepath
#-b can select log file path
# cp -r ./output_forecast/2020/10/07/. /mnt/forecast/forecast_img/geos5/2020/10/07/