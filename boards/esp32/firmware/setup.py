"""
HTTP-based setup over WLAN, configures sensor name, host, user login
"""
# TODO check unique first and then register sens
from machine import Pin, I2C
import time
import re
import json
import socket
import machine
from webtool import WebTool
import pages
import urequests as requests


import network

import socket

POST_HEADERS = {'content-type': 'application/json'}

class SensorConfig(WebTool):
    """Basic sensor configuration- host to push to, sensor name, and optional user login"""
    def __init__(self, sock, lock, config_file="config.json"):
        super().__init__(sock=sock, config_file=config_file)
        self.host = 0
        self.username = 0
        self.password = 0
        self.sensorname = 0
    def update_from_config(self):
        """Update progress (host, sensor name, login entered) from config file"""
        with open(self.config_file, "r") as config_file:
            config_data = json.load(config_file)
            if "host" in config_data:
                self.host = config_data["host"]
            if "username" in config_data:
                self.username = config_data["username"]
            if "sensorname" in config_data:
                self.sensorname = config_data["sensorname"]
    def update_config(self):
        """Update config file from instance variables"""
        with open(self.config_file, "r+") as config_file:
            config_data = json.load(config_file)
            tmp = config_data
            if self.host:
                config_data["host"] = self.host
            if self.username:
                config_data["username"] = self.username
                config_data["password"] = self.password
            if self.sensorname:
                config_data["sensorname"] = self.sensorname
            config_file.seek(0) # maybe unnecessary
            json.dump(config_data, config_file)
        if tmp != config_data:
            super().say("config updated!")


    @staticmethod
    def check_host_up(host):
        """Use the '/test' endpoint to check if the give host is up, returns the HTTP response"""
        resp = requests.get(str(host + "/test")).text
        if resp == "OK":
            return "OK"
        return str(resp)

    def name_sensor(self, desired_sensor_name):
        """
        Attempts to register a sensor with the given name at the host
        returns http code or error if it occurs
        """
        uname = json.dumps({"sensorname":desired_sensor_name})
        try:
            resp = requests.post(str(self.host + "/api/regSens"), headers = POST_HEADERS, data=uname).json()
            return resp["code"]
        except Exception as e:
            print('exceptioon occured in registering sensor!')
            print(e)
            return e

    def route_request(self, wanted_dir, params):
        """Takes the desired directory and returns the appropriate HTML page as a string"""
        page_to_return = 0
        if wanted_dir == "host":
            if 'host' in params:
                print("host in params!")
                if self.check_host_up(params['host']) == "OK":
                    print('host is up')
                    self.host = params['host']
                else:
                    page_to_return = pages.host_page(retry=True, hostentered=self.host)
            else:
                page_to_return = pages.host_page(hostentered=self.host)
        elif wanted_dir == "login":
            if self.host:
                page_to_return = pages.login_page()
        elif wanted_dir == "namesens":
            if self.host:
                if "sensorname" in params:
                    if self.sensorname:
                        page_to_return = pages.name_sensor(retry=False, sensnamed=self.sensorname, hostentered=self.host)
                    elif self.name_sensor(params["sensorname"]) == 200: # TODO maybe add the error message to the page / print to oled
                        self.sensorname = params["sensorname"]
                    else:
                        page_to_return = pages.name_sensor(retry=True, sensnamed=self.sensorname, hostentered=self.host)
                        # maybe I should put the pages as class methods
                else:
                    page_to_return = pages.name_sensor(retry=False, sensnamed=self.sensorname, hostentered=self.host)
            else:
                page_to_return = pages.name_sensor(retry=False, sensnamed=self.sensorname, hostentered=self.host)
        # elif wanted_dir == "startsampling":
        # TODO write sample lock handler

        self.update_config()
        if page_to_return:
            return page_to_return
        return pages.setup_home_page(host=self.host, uname=self.username, sname=self.sensorname)
    def run(self):
        """Handler user configuration through HTML pages"""
        print('starting config loop')
        print(self.sta.ifconfig())
        while True:
            super().say("http://" + str(self.sta.ifconfig()[0]))
            self.update_from_config()
            if self.host and self.sensorname:
                if self.config_lock.locked():
                    self.config_lock.release()
            conn, wanted_dir, params = super().recieve_request()
            while not self.config_lock.acquire():
                machine.idle()
            print("wanted dir is " +  str(wanted_dir))
            super().send_page(conn, self.route_request(wanted_dir, params))
            self.config_lock.release()
