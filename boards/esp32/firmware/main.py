"""
This file runs after boot.py on ESP32 boot.
Checks if I can conenct to WLAN from supplied config creds
If I can't, generate setup AP to get creds from user
Once I'm on WLAN, serve sensor configuration over WLAN
"""
import usocket as socket
from ap import SetupAp
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if True: # see if I can connect to WLAN
    setup = SetupAp(sock)
    setup.run()
