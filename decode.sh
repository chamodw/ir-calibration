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
PLOT=1 #  plot

SENSOR_DATA=session2_thu

PYTHON=python3.9



#Extract serial number from the lsusb output
ID=$(util/serial.sh)


# If serial number is empty, no sensor is connected
if [ -z "$ID" ] ; then
	echo "No sensor found"
	exit
fi


echo "--------------------------------"
echo "Sensor found with serial number $ID"



PORT=$(ls /dev | grep cu.usbmodem)
PORT=/dev/$PORT



unbuffer hexdump -v -e ' "" 5/2 "%4u " 3/4 " %4f " 2/2  "%4u "  "\n"'  $PORT  | awk '{print $4/100 " " $5*$5*$6/100000 + $5*$7 + $8 " " $5}'



