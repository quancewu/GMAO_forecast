#!/bin/bash
# echo $dayago daysago
# This script is using to chang file name auto_awesome
# quance wu 2020/12
path=/mnt/forecast/forecast_img
cd $path
echo "mypath: "$path
#!!!!!!!!!!select day!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
select='2020-07-01'                                 #!!
# echo $(date --date='2020-09-23 UTC')
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
year=$(date +'%Y');month=$(date +'%m');day=$(date +'%d')
year=$(date +'%Y' --date="$select UTC")
month=$(date +'%m' --date="$select UTC")
day=$(date +'%d' --date="$select UTC")
for month in {01..06}
do
    for i in {01..31}
    do
        echo $path/$year/$x/$i
        mv $path/geos5/$year/$month/$i/TotalAOD $path/geos5/$year/$month/$i/Total_AOD
        for name in Dust Smoke Total_AOD
        do
            # echo $name 
            for level in 500 700 850 925 1000
            do
                mv $path/geos5/$year/$month/$i/$name/${level}hpa $path/geos5/$year/$month/$i/$name/${level}hPa
                cd $path/geos5/$year/$month/$i/$name/${level}hPa
                pwd
                rename 's/TotalAOD/Total_AOD/' TotalAOD*
            done
        done
    done
done
echo $year,$month,$day
