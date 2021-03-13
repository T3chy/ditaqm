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
import cluster

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# so we don't need to hard reset in order to de/reallocate LAN resources
setup = SetupAp()
time.sleep(3)
if not setup.wlan_is_connected():
    setup.run(sock)
    setup.say("connected to wifi!")
    time.sleep(1)
    setup.say("rebooting...")
    setup.sta.disconnect()
    machine.reset()
lock = _thread.allocate_lock()
# config_lock.acquire() # lock until at least host and sensorname are configured
setup = SensorConfig(sock,lock)
_thread.start_new_thread(setup.run, ())
while not lock.acquire():
    pass
setup.reset_oled()

sensor_cluster = cluster.Cluster(setup.config)
# _thread.start_new_thread(
lock.release()

print('sensor time')
for i in range(30):
    time.sleep(5)
    print('sens')
    while not lock.acquire():
        machine.idle()
    print(sensor_cluster.detect_sensors())
    print(sensor_cluster.take_measurement())
    lock.release()
