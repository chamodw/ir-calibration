if [[ "$OSTYPE" == "darwin"* ]]; then
	util/serial_osx.sh
else
	util/serial_linux.sh
fi

