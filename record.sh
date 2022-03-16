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

PYTHON=python3.9

echo "--------------------------------"

TEMP1=$1
echo $TEMP1

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




PORT=$(ls /dev | grep cu.usbmodem)
PORT=/dev/$PORT

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

echo "\033[0;32m Good! ---------------------------"
cat $SENSOR_DATA/$ID/$TEMP1.txt >> $SENSOR_DATA/$ID/data.txt

exit 0

#--------------------------------------------------------------
# Rebuilding firmware
#--------------------------------------------------------------

( cd $MAKE_PATH && make clean )
( cd $MAKE_PATH && make all )

# Generate the DFU File

$ELF2DFU $(PWD)/$MAKE_PATH/Sensor_D11.elf $(PWD)/$SENSOR_DATA/$ID/out.dfu

# Flash the DFU file
echo "Flashing the new firmware. Please do not disconnect the sensor"

$DFU_UTIL -D $SENSOR_DATA/$ID/out.dfu
