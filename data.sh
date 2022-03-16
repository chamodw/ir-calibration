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

SENSOR_DATA=session2_thu

PYTHON=python3



#Extract serial number from the lsusb output
ID=$(util/serial.sh)


# If serial number is empty, no sensor is connected
if [ -z "$ID" ] ; then
	echo "No sensor found"
	exit
fi


echo "--------------------------------"
echo "Sensor found with serial number $ID"


# Look for all possible folders for this sensor
A=$(ls session2_thu | grep $ID)
#B=$(ls fri_data | grep $ID)

if [[ ! -z $A ]] ; then
	SENSOR_DATA=session2_thu
	echo "Session2 Thursday"
#else
#	SENSOR_DATA=fri_Data
#	echo "Friday"
fi



# Look for data in  different folders
ls session2_thu/$ID

#---------------------------------------------------------------
# Invoking Python script for calibration
#---------------------------------------------------------------

$PYTHON $CALIB_SCRIPT $(pwd)/$SENSOR_DATA/$ID/data.txt $PLOT 


