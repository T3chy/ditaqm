#!/bin/bash
# copyleft me (Elam) 2021; keep the software free, baby
# TODO get wifi creds and put em in the config
if [ "$(id -u)" != "0" ]; then
	echo "You must be the superuser to run this script :( try adding \"sudo\" at the begining of your command and rerun" >&2
	exit 1
fi

error() { clear; printf "ERROR:\\n%s\\n" "$1" >&2; exit 1;}
# pull deps
pullDeps(){
	pip install esptool
	pip-install pyserial
	apt install -y picocom
	apt install -y curl
	apt install -y jq
	pip install adafruit-ampy
}


# network tests
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
post_test(){
	resp=$(python postaqi.py firsttry)
	if [ "$resp" == "<Response [200]>" ]; then
		echo 0
	else
		echo "$resp"
	fi
}

# login / registration stuff
checkLogin(){
	curl -s -d "username=$1" -d "password=$2" -X POST "$host/api/login" | jq -r '.code'
}
regUser(){
	curl -s -d "username=$1" -d "password=$2" -X POST "$host/api/register" | jq -r '.code'
}
regSens(){
	curl -s -d "username=$1" -d "password=$2" -d "sensorname=$3" -X POST "$host/api/register" | jq -r '.code'
}



echo "Welcome to the DIYAQI autoinstallation script for the ESP8266 Microcontroller!"

echo "Pulling dependancies..."

pullDeps || error "dependancy pull failed!"

echo "dependancies pulled!"




echo "currently supported sensor(s); BME280 (i2c)" #, CJMCU-6814 (i2c, through ADS1115), and MH-Z19 (pwm connected to physical pin 7)" # lol not yet
echo "these sensors will automatically detected on boot, and their status will be accessible through your browser"

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
			if ! [ "$flag" == "y" ]; then
				echo "exiting..."
			fi
		fi
	fi
done

flag="n"
echo "Do you have a login? If not, we will create one shortly [y/N]"
read -r flag

code=1
if [ "$flag" == "y" ]; then
	while ! [ $code == 200 ]; do
		echo "What's your username?"
		read -r user
		echo "What's your password?"
		read -r pass
		code=$(checkLogin "$user" "$pass")
		if [ "$code" == 200 ]; then
			echo "login successful! Proceeding..."
		fi
		if [ "$code" == 400 ]; then
			echo "Please enter both a username and password!"
		fi
		if [ "$code" == 204 ]; then
			echo "Username and password do not match :("
		fi
		if [ "$code" == 206 ]; then
			echo "This username does not exist! Would you like to create an account with this username? [Y/n]"
			read -r cflag
			if ! [ "$cflag" == n ]; then
				flag="n"
				break
			fi
		fi
	done
fi
code=1
if ! [ "$flag" == "y" ]; then
	while ! [ $code == 200 ]; do

		echo "let's make you an account!"
		flag=1
		if [ -n "$user" ]; then
			flag=0
		fi
		while [ $flag -eq 1 ]; do
			echo "what do you want your username to be?"
			read -r user
			echo "you entered $user\. is that correct? [Y/n]"
			read -r flag
			if ! [ "$flag" == "n" ]; then
				flag=0
			else
				flag=1
			fi
		done
		echo "Welcome, $user\!"
		while [ $flag -eq 1 ]; do
			echo "Please enter a password"
			read -r pass
			echo "you entered $pass\. is that correct? [Y/n]"
			read -r flag
			if ! [ "$flag" == "n" ]; then
				flag=0
			else
				flag=1
			fi
		done
		echo "attempting to register user..."
		code=$(regUser user pass)
		if [ "$code" == 200 ]; then
			echo "Registration successful! Proceeding..."
		fi
		if [ "$code" == 206 ]; then
			echo "user already exists :( please choose a unique username"
		fi
		if [ "$code" == 400 ]; then
			echo "an unknown error occured :( super bummer"
		fi
	done
fi

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
				echo "Your sensor name is unique!"
				echo "Registering sensor..."
				code=$(regSens user pass name)

			else
				echo "Someone already snagged that name :( please try a different one"
			fi

		fi

	else
		echo "your entry \($name\) did not meet the requirements :( please try again"
	fi
done

echo "pulling dependancies..."
pullDeps || error "failed to pull dependancies"

echo "saving configuration..."

jq -n '{"host":'\""$host"\"', "sensorname":'\""$name"\"', "username":'\""$user"\"', "password":'\""$pass"\"'}' > config.json

echo "erasing flash on device..."
esptool.py --port /dev/ttyUSB0 erase_flash


echo "pulling Micropython firmware..."
cat firmware.bin > /dev/null || wget -O firmware.bin "https://micropython.org/resources/firmware/esp8266-20200911-v1.13.bin"
echo "flashing firmware..."

echo "copying source files to device..."

ampy --port /dev/ttyUSB0 --baud 115200 put boot.py
echo "boot script copied!"
ampy --port /dev/ttyUSB0 --baud 115200 put tests.py
echo "sensor tests script copied!"
ampy --port /dev/ttyUSB0 --baud 115200 put config.json
echo "config script copied!"
ampy --port /dev/ttyUSB0 --baud 115200 put BME280.py
echo "BME support script copied!"
ampy --port /dev/ttyUSB0 --baud 115200 put main.py
echo "main script copied!"
echo "everything should be set up! Reboot (unplug and replug) your device to start POSTing!"
