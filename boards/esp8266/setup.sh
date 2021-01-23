#!/bin/bash
# copyleft me (Elam) 2021; keep the software free, baby
if [ "$(id -u)" != "0" ]; then
	echo "You must be the superuser to run this script :( try adding \"sudo\" at the begining of your command and rerun" >&2
	exit 1
fi
# pull deps
echo "pulling dependancies..."
sudo pip install esptool
sudo esptool.py --port /dev/ttyUSB0 erase_flash
sudo apt install picocom
pip install adafruit-ampy

echo "pulling Micropython firmware..."
cat firmware.bin > /dev/null || wget -O firmware.bin "https://micropython.org/resources/firmware/esp8266-20200911-v1.13.bin"
echo "flashing firmware..."
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect -fm dio 0 "firmware.bin"

wait $!
sleep 5
echo "copying source files to device..."

ampy --port /dev/ttyUSB0 --baud 115200 put boot.py
echo "boot script copied!"
ampy --port /dev/ttyUSB0 --baud 115200 put BME280.py
echo "BME script copied!"
ampy --port /dev/ttyUSB0 --baud 115200 put main.py
echo "main script copied!"

echo "entering live prompt. Enter ctrl-a and then ctrl-x to exit"
picocom /dev/ttyUSB0 -b115200
