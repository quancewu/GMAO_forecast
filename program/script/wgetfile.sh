#!/usr/bin/bash
#Program:
#   download GEOS file using wget
# 2020/10/09
initdaysago=2
echo init $initdaysago daysago
read -t5 -p 'select day: ' dayago
if $dayago
then dayago=$initdaysago
    echo no input value
fi
path=/data/GEOS5/
cd $path
# python3 ./get_data_fromftp.py $dayago
python3 ./program/getfile_txt.py $dayago

echo "mypath: "$path
echo "Hi, I'm sleeping for 5 seconds..."
year=$(date +'%Y' --date="-$dayago day")
month=$(date +'%m' --date="-$dayago day")
day=$(date +'%d' --date="-$dayago day")
echo $day $month $year 
# sleep 5
filepath=portal.nccs.nasa.gov/datashare/gmao_ops/pub/fp/das/Y$year/M$month/D$day/downloadfile.txt
echo $filepath
wget -x -bq -nv -i $path$filepath
# wget -x -nv -i $path$filepath

#-b can select log file path