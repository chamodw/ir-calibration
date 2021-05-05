#!/bin/zsh


#	
#	Chamod Weerasinghe
#	Calibration scirpt version 2
#	1. Script looks for USB devices and identifies temperature sensor is connected
#	2. Creates a folder with the serial number of the sensor
#	3. Takes readings from the sensor in 3 stages for 3 different temperatures
#	
#	


TIMEOUT=5 # Specifies the data collection time for each temperature point

SRC_PATH=sensor-build/kiwrious-sensor/src
MAKE_PATH=sensor-build
ELF2DFU=elf2dfu/elf2dfu
DFU_UTIL=dfu-util
CALIB_SCRIPT=calibration/calibration.py
PLOT=2 #  plot level

SENSOR_DATA=wed_data

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



PORT=$(ls /dev | grep cu.usbmodem)
PORT=/dev/$PORT

#Create a unique folder for data collection 
mkdir $SENSOR_DATA/$ID




#---------------------------------------------------------------
# Invoking Python script for calibration
#---------------------------------------------------------------

$PYTHON $CALIB_SCRIPT $(pwd)/$SENSOR_DATA/$ID/data.txt $(pwd)/$SRC_PATH/ir_constants.h $PLOT

