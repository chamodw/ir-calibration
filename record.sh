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
PLOT=0

SENSOR_DATA=session2_thu

PYTHON=python3

echo "--------------------------------"

TEMP1=$1
echo $TEMP1
if [ -z "$TEMP1" ] ; then
	echo "Usage ./record.sh temprature (./record.sh 25)"
	exit
fi


#Extract serial number using the support script
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
	echo "Session 2 Thursday"
#else
#	SENSOR_DATA=fri_Data
#	echo "Friday"
fi




PORT=$(util/port.sh)

#Create a unique folder for data collection 
mkdir $SENSOR_DATA/$ID



# ----------------------------------------------------------------
# Data collection for temperature point 1
#-----------------------------------------------------------------

timeout $TIMEOUT  unbuffer hexdump -v -e " \"$TEMP1, \" 13/2 \"%6u, \"  \"\n\" " $PORT  >> $SENSOR_DATA/$ID/$TEMP1.txt



#---------------------------------------------------------------
# Invoking Python script for calibration
#---------------------------------------------------------------

$PYTHON $CALIB_SCRIPT $(pwd)/$SENSOR_DATA/$ID/$TEMP1.txt $PLOT 

#If python script returns error, delete the data collected in
#this invocation
RET=$?
if [ $RET -ne 0 ] ; then
	rm $(pwd)/$SENSOR_DATA/$ID/$TEMP1.txt
	exit 1
fi

#If python script returns success, append this data to the 
#sensor data file

echo "\033[0;32m Good! ---------------------------\033[0m"
# no longer merges to one file, this happens at the processing step
#cat $SENSOR_DATA/$ID/$TEMP1.txt >> $SENSOR_DATA/$ID/data.txt 

exit 0

