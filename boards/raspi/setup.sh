#!/bin/bash
# copyleft me (Elam) 2021; keep the software free, baby
# TODO check if a config file already exists
if [ "$(id -u)" != "0" ]; then
	echo "You must be the superuser to run this script :( try adding \"sudo\" at the begining of your command and rerun" >&2
	exit 1
fi

error() { clear; printf "ERROR:\\n%s\\n" "$1" >&2; exit 1;}

pullDeps(){ #TODO try to not run this after reboot

	# git, cuz duh
	apt-get install -y git

	# try to not repull deps
	[ -d diyaqi/boards/raspi ] || git clone https://github.com/t3chy/diyaqi
	cd diyaqi/boards/raspi || error "can't enter source directory. Git clone probably failed"
	if ! [ -f ran ]; then {
		touch ran

		apt-get update || error "apt-get update failed! Is your package cache corrupted? see troubleshooting"


		# python, for obvious reasons
		apt-get install -y python3 python3-pip || error "Couldn't install python"
		pip3 install --upgrade setuptools

		#make python3 default
		update-alternatives --install /usr/bin/python python "$(which python2)" 1
		update-alternatives --install /usr/bin/python python "$(which python3)" 2

		# cURL to test website continuity and name uniqueness

		apt-get install -y curl

		# i2ctools to detect device

		apt-get install -y i2c-tools

		# jq for json-based config file
		apt-get install -y jq

		# i2c stuff
		pip3 install RPI.GPIO || exit 1
		pip3 install adafruit-blinka
		pip3 install adafruit-circuitpython-bme280
		pip3 install adafruit-circuitpython-ads1x15
		pip3 install pigpio

		# pwm for the mhz19b
		apt-get install -y pigpio python-pigpio python3-pigpio
		sudo systemctl enable pigpiod || error "failed to enable pigpiod!"
		sudo systemctl start pigpiod || error "failed to start pipgpiod!"
	}
	# else { maybe this should be used
	# 	rm ran
	# }
	fi


}

# i2c stuff
i2cDeviceExists() {
	devs=$(i2cdetect -y 1 | sed 1d | sed 's/^....//' | sed 's/--//g')
	case $devs in
		(*[![:blank:]]*) return 0;;
		(*) return 1
	esac
}
enableI2c(){
	if ! i2cdetect -y 1 > /dev/null; then
		echo "i2c-bcm2708" >> /etc/modules
		echo "i2c-dev" >> /etc/modules
		echo "dtparam=i2c_arm=on" >> /boot/config.txt
		echo "dtparam=i2c1=on" >> /boot/config.txt
		echo 1
	else
		echo 0
	fi
}

# various sensor tests
test_bme(){ python tests/test_bme280.py; }
test_cjmcu(){ python tests/test_cjmcu_ads1115.py; }
test_mhz19b(){ python tests/test_mhz19b.py; }

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


cd /home/pi || error "cd failed ???"

echo "Welcome to the PiAQI autoinstallation script!"

echo "Pulling dependancies..."

pullDeps || error "dependancy pull failed!"

echo "dependancies pulled!"

if [ "$(enableI2c)" -eq 1 ]; then
	read -r -p "i2c has just been enabled. We now need to reboot (you will be disconnected). Press enter to continue, and then rerun this script with \"sudo ./setup.sh\" once you reconnect"
	reboot
fi


cat << "EOF"
Wire your BME sensor according to the following key
_______________________
|Sensor     |Pi       |
|---------------------|
|VCC/V+/VIN |V        |
|GND        |G        |
|SDA        |D        |
|SCL        |C        |
|---------------------|

(not to scale, top left pin is pin #1)
.____________.
|h   sd   .V |
|d        D. |
|m        C. |
|i        .. |
|         G. |
|         .. |
|u        .. |
|s        .. |
|b        .. |
|u        .. |
|s        .. |
|b        .. |
|____________|

EOF

echo "currently supported sensors; BME280 (i2c), CJMCU-6814 (i2c, through ADS1115), and MH-Z19 (pwm connected to physical pin 7)"
read -r -p "Please hook up the sensors you would like to use and press enter to continue"

echo "Looking for BME280 Sensor..."

bme="$(test_bme)"
if [ "$bme" == 0 ]; then
	echo "BME sensor found!"
	bme=1
else
	echo "no BME sensor found :("
	bme=0
fi

echo "Looking for CHMCU-6814 Sensor..."
cjmcu="$(test_cjmcu)"
if [ "$cjmcu" == 0 ]; then
	echo "CHMCU-6814 sensor found!"
	cjmcu=1
else
	echo "CHMCU-6814 no sensor found :("
	cjmcu=0
fi


echo "Looking for CHMCU-6814 Sensor..."
mhz19b="$(test_mhz19b)"
if [ "$mhz19b" == 0 ]; then
	echo "mhz19b sensor found!"
	mhz19b=1
else
	echo "no mhz19b sensor found :("
	mhz19b=0
fi


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
regSens(){
	curl -s -d "username=$1" -d "password=$2" -d "sensorname=$3" -X POST "$host/api/register" | jq -r '.code'
}
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
				code=$(regSens user pass name)"

			else
				echo "Someone already snagged that name :( please try a different one"
			fi

		fi

	else
		echo "your entry \($name\) did not meet the requirements :( please try again"
	fi
done

echo "saving configuration..."

jq -n '{"host":'\""$host\""', "sensorname":'\""$name"\"', "username":'\""$user"\"', "password":'\""$pass"\"', "BME":'\""$bme"\"', "CJMCU":'\""$cjmcu"\"', "MHZ19B":'\""$mhz19b"\"'}' > config.json


echo "configuration stored!"

echo "attempting to make a POST request..."

try=$(post_test)
if [ "$try" -eq 0 ]; then
	echo "success! enabling automatic restart on boot"
else
	echo "failure, see error trace above :( exiting...."
	echo "$try"
	exit 1
fi

echo "changing script permissions..."

chmod +x postaqi.py || error "changing permissions failed!"

echo "creating service..."

cat serviceunit > /etc/systemd/system/postaqi.service || error "creating service failed :("

echo "service created with a name of \"postaqi\"! Enabling..."

systemctl enable postaqi.service || error "failed to emable script :("

echo "service enabled! reloading daemon...."

systemctl daemon-reload || error "failed to reload daemon :("

echo "daemon reloaded! starting service..."

systemctl start postaqi.service || error "failed to start service :("

echo "service started! you can check its status by running \"sudo systemctl status postaqi.service\" everything is now set up! Put this Pi Sensor combo somewhere safe, and have a great day!"

exit 0
