#!/bin/bash
# copyleft me (Elam) 2021; keep the software free, baby
# TODO get wifi creds and put em in the config
if [ "$(id -u)" != "0" ]; then
	echo "You must be the superuser to run this script :( try adding \"sudo\" at the begining of your command and rerun" >&2
	exit 1
fi

error() { clear; printf "ERROR:\\n%s\\n" "$1" >&2; exit 1;}
hostTest(){
	resp=$(curl -o /dev/null -i -L -s -w "%{http_code}\n" "$host/test")
	if [ "$resp" == 200 ]; then
		echo 0
	else
		echo 1
	fi
}

checkUnique(){
	resp=$(curl -o /dev/null -i -L -s -w "%{http_code}\n" -d "name=$1" -X POST "$host/checkUnique")
	if [ "$resp" == 200 ]; then
		echo 0
	else
		echo 1
	fi
}
# pull deps
echo "pulling dependancies..."
sudo pip install esptool
sudo esptool.py --port /dev/ttyUSB0 erase_flash
sudo apt install picocom
pip install adafruit-ampy



echo "pulling Micropython firmware..."
cat firmware.bin > /dev/null || wget -O firmware.bin "https://micropython.org/resources/firmware/esp8266-20200911-v1.13.bin"
echo "flashing firmware..."
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect -fm dio 0 "firmware.bin" || error "failure flashing firmware!"


flag=1
while [ $flag -eq 1 ]; do
	echo "Please enter the url provided by the organizer ex. https://albanylovestheair.com"
	read -r host
	echo "you entered $host is this correct? [Y/n]"
	read -r flag
	if [ "$flag" == "n" ]; then
		flag=0
	else
		flag=1
	fi
	if [ $flag -eq 1 ]; then
		echo "testing host..."
		if [ "$(hostTest)" -eq 0 ]; then
			echo "host is up!"
			flag=0
		else
			echo "host is not up :( retry? [y/N]"
			read -r flag
			if [ "$flag" == "y" ]; then
				flag=0
			else
				echo "exiting..."
				exit 1
			fi
		fi
	fi
done

flag=1
while ! [ $flag -eq 0 ]; do
	echo "enter what you'd like your sensor to be called. Please make it only upper and lower case letteers, numbers, and no spaces. Ex. \"ElamHouse1\""
	read -r name
	if [[ $name == *[a-zA-Z0-9]* ]]; then
		echo "you entered $name is this correct? [Y/n]"
		read -r flag
		if [ "$flag" == "n" ]; then
			flag=0
		else
			flag=1
		fi

		if ! [ "$flag" -eq 0 ]; then
			echo "checking uniqueness..."
			flag=$(checkUnique "$name")

			if [ "$flag" -eq 0 ]; then
				echo "Your sensor name is unique! Proceeding..."
			else
				echo "Someone already snagged that name :( please try a different one"
			fi

		fi

	else
		echo "your entry \($name\) did not meet the requirements :( please try again"
	fi
done

echo "writing config..."
printf "%s\n%s\n" "$host" "$name" > config
echo "detecting sensors..."
python tests.py

echo "copying source files to device..."

ampy --port /dev/ttyUSB0 --baud 115200 put boot.py
echo "boot script copied!"
ampy --port /dev/ttyUSB0 --baud 115200 put config
echo "config script copied!"
ampy --port /dev/ttyUSB0 --baud 115200 put BME280.py
echo "BME support script copied!"
ampy --port /dev/ttyUSB0 --baud 115200 put main.py
echo "main script copied!"
echo "everything should be set up! Reboot (unplug and replug) your device to start POSTing!"
