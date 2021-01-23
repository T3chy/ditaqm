# pull deps
sudo pip install esptool
sudo esptool.py --port /dev/ttyUSB0 erase_flash
sudo apt install picocom
pip install adafruit-ampy
pull micropython bin #TODO make this an actual command

esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect -fm dio 0 <bin filename>
git clone https://github.com/psf/requests
sudo ampy --port /dev/ttyUSB0 --baud 115200 put boot.py
sudo ampy --port /dev/ttyUSB0 --baud 115200 put BME280.py


sudo picocom /dev/ttyUSB0 -b115200
