#!/bin/zsh

clear
#	
#	Chamod Weerasinghe
#	Data inspection script
#	Calculates standard deviation and highlights errors
#	


TIMEOUT=5 # Specifies the data collection time for each temperature point

SRC_PATH=sensor-build/kiwrious-sensor/src
MAKE_PATH=sensor-build
ELF2DFU=elf2dfu/elf2dfu
DFU_UTIL=dfu-util
CALIB_SCRIPT=calibration/calibration.py
PLOT=0 #  plot level

SENSOR_DATA=fri_data

PYTHON=python3.9



#Extract serial number from the lsusb output
ID=$(lsusb 2> /dev/null | grep "Kiwrious Temperature" | awk '{print $NF}' )


# If serial number is empty, no sensor is connected
if [ -z "$ID" ] ; then
	echo "No sensor found"
	exit
fi


echo "--------------------------------"
echo "Sensor found with serial number $ID"


# Look for all possible folders for this sensor
A=$(ls wed_data | grep $ID)
B=$(ls fri_data | grep $ID)

if [[ ! -z $A ]] ; then
	SENSOR_DATA=wed_data
	echo "Wednesday"
else
	SENSOR_DATA=fri_Data
	echo "Friday"
fi




PORT=$(ls /dev | grep cu.usbmodem)
PORT=/dev/$PORT


# Look for data in  different folders
ls data_tue/$ID
ls wed_data/$ID
ls fri_data/$ID

#---------------------------------------------------------------
# Invoking Python script for calibration
#---------------------------------------------------------------

$PYTHON $CALIB_SCRIPT $(pwd)/$SENSOR_DATA/$ID/data.txt $PLOT 


