"""
An inital access Point generated when there are no WAN network credentials configured
"""
import machine
from machine import Pin, I2C
import time
import re
import json
import ssd1306
import os
import pages
from webtool import WebTool



# ************************
# Configure the ESP32 wifi
# as Access Point mode.
import network

class SetupAp(WebTool):
    def __init__(self, sock):
        super().__init__(self, sock)
        super().setup_ap()
        super().get_html_ssid_list()
    def run(self):
        super().recieve_request()


# ************************
# Configure the socket connection
# over TCP/IP

import socket


# ************************
# Functions for creating the
# web pages to be displayed



    while True:
        if sta.isconnected():
            break
        say("http://" + str(ap.ifconfig()[0]))
        conn, addr = s.accept()
        request=conn.recv(1024)
        # print("Content %s" % str(request))
        ssid = None
        passwd = None
        request = str(request, 'utf8')
        if sta.isconnected():
            finish(conn)
            break
        if "GET /?ssid=" in request:
            print('ssid request time')
            try:
                ssid = re.search(r"ssid=(.*?)\&", request).group(1).strip()
                passwd = re.search(r"pass=(.*?)\ HTTP", request).group(1).strip()
                if ssid and passwd:
                    print("ssid:", ssid)
                    print("pass:", passwd)
                    sta.connect(str(ssid), str(passwd))
                    finish(conn)
                    break
            except Exception as e:
                print(e)

        # Socket send()
        try: # we sometimes this fails when the user closes web browser prematurely
            response = web_page()
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()
        except Exception as e:
            print("sending response failed!")
            print(e)
            pass
    with open("config.json", "w") as f:
        data = {}
        data["ssid"] = ssid
        data["passwd"] = passwd
        json.dump(data, f)
        say("Config stored,", snd="connected to WLAN!")
    machine.reset()

else:
    say("connected to WLAN!")
