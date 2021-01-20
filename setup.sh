#!/bin/bash
# copyleft me (Elam) 2021; keep the software free, baby
if [ "$(id -u)" != "0" ]; then
	echo "You must be the superuser to run this script :( try adding \"sudo\" at the begining of your command and rerun" >&2
	exit 1
fi
error() { clear; printf "ERROR:\\n%s\\n" "$1" >&2; exit 1;}
i2cDeviceExists() {
	devs=$(i2cdetect -y 1 | sed 1d | sed 's/^....//' | sed 's/--//g')
	case $devs in
		(*[![:blank:]]*) return 0;;
		(*) return 1
	esac
}
pulldeps(){
	apt-get update || error "apt-get update failed! Is your package cache corrupted? see troubleshooting"
	# git, cuz duh
	apt-get install -y git

	cd diyaqi || git clone https://github.com/t3chy/diyaqi && cd diyaqi

	# python, for obvious reasons
	apt-get install -y python3 python3-pip || exit 1
	pip3 install --upgrade setuptools

	#make python3 default
	update-alternatives --install /usr/bin/python python "$(which python2)" 1
	update-alternatives --install /usr/bin/python python "$(which python3)" 2

	# cURL to test website continuity and name uniqueness

	apt-get install -y curl

	# i2ctools to detect device
	apt-get install -y i2c-tools

	# sensor / boardio deps

	pip3 install RPI.GPIO || exit 1
	pip3 install adafruit-blinka
	pip3 install adafruit-circuitpython-bme280
	pip3 install adafruit-circuitpython-ads1x15
	pip3 install pigpio
	apt-get install -y pigpio python-pigpio python3-pigpio
	sudo systemctl enable pigpiod || error "failed to enable pigpiod!"
	sudo systemctl start pigpiod || error "failed to start pipgpiod!"

}
enablei2c(){
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
bmeTest(){
	python tests/bme280Test.py
}
cjmcuTest(){
	python tests/cjmcuADS1115Test.py
}
mhz19bTest(){
	python tests/mhz19Test.py
}
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
testPost(){
	resp=$(python postaqi.py firsttry)
	if [ "$resp" == "<Response [200]>" ]; then
		echo 0
	else
		echo "$resp"
	fi
}
cd /home/pi || error "cd failed ???"

echo "Welcome to the PiAQI autoinstallation script!"

echo "Pulling dependancies..."
pulldeps || error "dependancy pull failed!"

echo "dependancies pulled!"

if [ "$(enablei2c)" -eq 1 ]; then
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
bme="$(bmeTest)"
if [ "$bme" == 0 ]; then
	echo "BME sensor found!"
else
	echo "no BME sensor found :("
fi

echo "Looking for CHMCU-6814 Sensor..."
cjmcu="$(cjmcuTest)"
if [ "$cjmcu" == 0 ]; then
	echo "CHMCU-6814 sensor found!"
else
	echo "CHMCU-6814 no sensor found :("
fi


echo "Looking for CHMCU-6814 Sensor..."
mhz19b="$(mhz19bTest)"
if [ "$mhz19b" == 0 ]; then
	echo "mhz19b sensor found!"
else
	echo "no mhz19b sensor found :("
fi


flag=1
while ! [ $flag -eq 0 ]; do
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

printf "%s\n%s\n%d\n%d\n%d\n" "$host" "$name" "$bme" "$cjmcu" "$mhz19b" > config

echo "configuration stored!"

echo "attempting to make a POST request..."

try=$(testPost)
if [ "$try" -eq 0 ]; then
	echo "success! enabling automatic restart on boot"
else
	echo "failure, see error trace below :( exiting...."
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
