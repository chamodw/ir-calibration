lsusb 2> /dev/null | grep "Kiwrious Temperature" | awk '{print $NF}'

