"""
This file runs after boot.py on ESP32 boot.
Checks if I can conenct to WLAN from supplied config creds
If I can't, generate setup AP to get creds from user
Once I'm on WLAN, serve sensor configuration over WLAN
"""
import _thread
import time
import usocket as socket
from ap import SetupAp
from setup import SensorConfig
import machine
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# so we don't need to hard reset in order to de/reallocate LAN resources
setup = SetupAp()
time.sleep(3)
if not setup.wlan_is_connected():
    setup.run(sock)
    setup.say("connected to wifi!")
    time.sleep(1)
    setup.say("rebooting...")
    machine.reset()
print('ap over, wlan time')
config_lock = _thread.allocate_lock()
# config_lock.acquire() # lock until at least host and sensorname are configured
setup = SensorConfig(sock,config_lock)
_thread.start_new_thread(setup.run, ())
while not config_lock.acquire():
    pass
print('configed!')
