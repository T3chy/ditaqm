json.dumpo# TODO check unique first and then register sens
import machine
from machine import Pin, I2C
import time
import re
import json
import socket
import urequests as requests


# ************************
# Configure the ESP32 wifi
# as Access Point mode.
import network

sta = network.WLAN(network.STA_IF)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if not sta.active():
    sta.active(True)
    while not sta.active():
        pass
print('network config:', sta.ifconfig())


# ************************
# Configure the socket connection
# over TCP/IP
import socket

# AF_INET - use Internet Protocol v4 addresses
# SOCK_STREAM means that it is a TCP socket.
# SOCK_DGRAM means that it is a UDP socket.

# ************************
# Function for creating the
# web page to be displayed

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sta = network.WLAN(network.STA_IF)
class SensorConfig(WebTool):
    """Basic sensor configuration- host to push to, sensor name, and optional user login"""
    def __init__(self, sta, sock, config_file="config.json"):
        WebTool.__init__(self, sta, sock, config_file)
        self.host = 0
        self.username = 0
        self.sensorname = 0
    def update_from_config(self):
        """Update progress (host, sensor name, login entered) from config file"""
        with open(self.config_file, "r") as config_file:
            config_data = json.load(config_file)
            if "host" in config_data:
                self.host = config_data["host"]
            if "username" in config_data:
                self.uname = config_data["username"]
            if "sensorname" in config_data:
                self.host = config_data["sensor"]





        response = main_page()

        print("args: " + str(args))
        if wanted == "login":
            response = login_page()
        elif wanted == "host":
            print(wanted)
            if "host" in args:
                print(args['host'])
                try:
                    resp = requests.get(str(args["host"] + "/test")).text
                except Exception as e:
                    print(e)
                    resp = 0
                if resp == "OK":
                    hostentered = True
                    HOST = args["host"]
                    response = main_page()
                    with open('config.json', 'r+') as f:
                        content = json.load(f)
                        content["host"] = args["host"]
                        f.seek(0)
                        json.dump(content,f)
                        print("host added to configuration!")
                else:
                    response = host_page(retry=True)
            else:
                response = host_page(retry=False)
        elif wanted == "reset":
            reset_settings()
        elif wanted == "namesens":
            if not hostentered:
                response = main_page()
            elif "sensname" in args:
                print(args['sensname'])
                try:
                    uname = json.dumps({"sensorname":args['sensname']})
                    resp = requests.post(str(HOST + "/api/regSens"), headers = {'content-type': 'application/json'}, data=uname).json()
                    print("registering sensor reponse: " + str(resp))
                    if resp["code"] == 200:
                        with open('config.json', 'r+') as f:
                            content = json.load(f)
                            content["sensname"] = args["sensname"]
                            f.seek(0)
                            json.dump(content,f)
                            print("sensor name added to configuration!")
                        sensnamed = True
                        SNAME = args["sensname"]
                        response = main_page()
                    else:
                        response = sensname_page(retry=True)
                except Exception as e:
                    print("error in registering sensor: ")
                    print(e)
                    print(resp)
                    response = sensname_page(retry=True)
            else:
                response = sensname_page(retry=False)



print('serving')
flag = sta.isconnected()
if not flag:
    try:
        with open("config.json", "r") as f:
            try:
                data = json.load(f)
                sta.connect(str(data["ssid"]), str(data["passwd"]))
                counter = 0
                while not sta.isconnected():
                    time.sleep(1)
                    counter += 1
                    if counter > 5:
                        break
                if sta.isconnected():
                    print('isconnected')
                    flag = 1
            except Exception as e:
                print("failed  to write config! rebooting...")
                print(e)
    except:
        pass
if not flag:
    machine.reset()

while True:
    print_config()
    hostentered = False
    loggedin = False
    sensnamed = False

    HOST= "NA"
    UNAME = "NA"
    SNAME = "NA"
    with open("config.json", "r") as f:
        f.seek(0)
        data = json.load(f)
        if "host" in data:
            hostentered = True
            HOST = data["host"]
        if "username" in data and "password" in data:
            loggedin = True
            UNAME = data["username"]
        if "sensname" in data:
            sensnamed = True
            SNAME = data["sensname"]
    request = str(request, 'utf8')
    if request != "":
        try:
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()
        except: #this is probably bad don't do this
            pass
        else:
            pass
