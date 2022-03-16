if test -e /dev/ttyACM0; then
	/bin/udevadm info --name=/dev/ttyACM0 | grep SERIAL_SHORT | sed 's/.*=//'
fi
