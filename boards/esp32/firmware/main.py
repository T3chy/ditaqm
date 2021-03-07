"""
This file runs after boot.py on ESP32 boot.
Checks if I can conenct to WLAN from supplied config creds
If I can't, generate setup AP to get creds from user
Once I'm on WLAN, serve sensor configuration over WLAN
"""
import usocket as socket
from ap import SetupAp
from setup import SensorConfig
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# so we don't need to hard reset in order to de/reallocate LAN resources
setup = SetupAp()
if not setup.wlan_is_connected():
    setup.run(sock)
print('ap over wlan time')
setup = SensorConfig(sock)
setup.run()
