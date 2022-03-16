if [[ "$OSTYPE" == "darwin"* ]]; then
	echo /dev/$(ls /dev | grep cu.usbmodem)
else
	echo /dev/ttyACM0
fi

