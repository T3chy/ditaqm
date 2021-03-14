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
def sample(clust, lock, interval=30):
    """
    Send periodic measurements from connected sensors, exits when the provided lock is acquired
    """
    # lock is released when user decides to start
    # to be implemented, lol
    while not lock.acquire():
        pass
    lock.release()
    while True:
        clust.send_sample()
        time.sleep(interval)
        if lock.locked():
            break


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
setup = SetupAp()

if not setup.wlan_is_connected():
    # launch setup AP and get valid wifi creds, then reboot
    setup.run(sock)
    setup.say("connected to wifi!")
    time.sleep(1)
    setup.say("rebooting...")
    setup.sta.disconnect()
    machine.reset()

config_lock = _thread.allocate_lock()
sample_lock = _thread.allocate_lock()
config_lock.acquire()
# lock until at least host and sensorname are configured, so we have somewhere to push

setup = SensorConfig(sock,config_lock)
# keeps lock until host and sensorname are entered
#takes and releases lock as config is being read / pages are being sent
_thread.start_new_thread(setup.run, ())

while not config_lock.acquire():
    pass

setup.reset_oled()

# init sensors
sensor_cluster = cluster.Cluster(setup.config)
config_lock.release()

print('sensor time')
_thread.start_new_thread(sample, (sensor_cluster, sample_lock))
if input("kill sampling? [Y/n] \n") != "n":
    sample_lock.acquire()
