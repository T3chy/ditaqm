"""
Parent class used to assist in wireless setup
"""
import json
import time
import re
import ssd1306
import usocket as socket
import network
from machine import Pin, I2C
import os


class WebTool:
    """said parent class"""
    def __init__(self, sock, config_file="config.json"):
        sta = network.WLAN(network.STA_IF)
        sta.active(False)
        sta.active(True)
        while not sta.active():
            pass
        self.sta = sta
        self.ap = None
        self.ssid = None
        self.passwd = None
        self.config_file = config_file
        self.sock = sock
        sock.bind(('',80)) # socket is reachable by any address the machine happens to have
        sock.listen(5)     # max of 5 socket connections
        self.i2c = I2C(-1, Pin(5), Pin(4))
        try:
            self.oled = ssd1306.SSD1306_I2C(128, 32, self.i2c)
        except:
            self.oled = None
        self.dns_addr = socket.getaddrinfo("127.0.0.1", 53)[0][-1]
        if not os.path.exists(config_file):  # create config if it doesn't exist
            with open(config_file, "w") as f:
                pass
        # for DNS lookups
    def scan_ssids(self):
        """Scans local networks and returns an array of SSIDs"""
        self.say("Scanning local SSIDs...")
        return [net[0] for net in self.sta.scan()]
    def get_html_ssid_list(self):
        """Returns an HTML string containing dropdown menu with connectable SSIDs"""
        ssid_list = "<select id=\"ssid\" name=\"ssid\">"
        for ssid in self.scan_ssids():
            ssid = str(ssid).strip('b').strip('\'').strip("\"")
            ssid_list += "<option value= \"" + ssid + "\">" + ssid + "</option>"
        ssid_list +=  "</select>"
        return ssid_list

    def setup_ap(self, ssid='cluster', passwd='12345678'):
        """Sets up an Access Point and prints creds to OLED"""
        self.ssid = ssid
        self.passwd = passwd
        ap = network.WLAN(network.AP_IF)
        ap.active(False)
        ap.active(True)
        ap.config(essid=ssid, password=passwd)
        while not ap.active():
            pass
        self.ap = ap
        self.say(str("ssid:"+ssid+"  pass:"+passwd))
        time.sleep(5) # so user can at least glance oled message
        self.say("http:// " + str(self.ap.ifconfig()[0]))

    def reset_oled(self):
        """Blank the optionally attached oled screen"""
        if self.oled:
            self.oled.fill(0)
            self.oled.show()
    def say(self, msg):
        """Print a given message to the optionally attached oled screen, 15 chars per line"""
        if self.oled:
            self.reset_oled()
            self.oled.text(str(msg[0:14], 0, 0)) # 1st line
            self.oled.text(str(msg[15:], 0, 10)) # 2nd line
            self.oled.show()
        print("printing \"" + str(msg) + "\" to oled")

    @property
    def wlan_is_connected(self):
        """Return if the device is connceted to WLAN"""
        return self.sta.isconnected()
    @property
    def read_config(self):
        """return the config json file as a dictionary"""
        with open(self.config_file, "r") as config_file:
            config_data = json.load(config_file)
        return config_data
    def connect_to_wlan(self, ssid=None, passwd=None):
        """Attempt to connect to the given ssid with the given password, defaults to config"""
        if ssid and passwd:
            self.sta.connect(str(ssid), str(passwd))
        else:
            with open(self.config_file, 'r') as config_file:
                config_data = json.load(config_file)
                if "ssid" in config_data and "passwd" and config_data:
                    self.sta.connect(str(config_data["ssid"]), str(config_data["passwd"]))
                else:
                    return 0
        counter = 0
        while not self.sta.isconnected():
            time.sleep(1)
            counter += 1
            if counter > 5:
                break
        if self.sta.isconnected():
            return self.sta.ifconfig()[0]
        return 0
    def write_config(self, data_to_write):
        """Updates the config file with key-values given in data_to_write"""
        with open(self.config_file, "r+") as config_file:
            config_data = json.load(config_file)
            for key in data_to_write:
                config_data[key] = data_to_write[key]
            json.dump(config_data, config_file)
    def reset_config(self, reset_wlan_too=False):
        """Resets user config file, keeps wlan credentials unless reset_wlan_too"""
        if reset_wlan_too:
            with open(self.config_file, "r+") as config_file:
                config_data = json.load(config_file)
            data_to_write = {config_data["ssid"], config_data["passwd"]}
        else:
            data_to_write = {}
        with open(self.config_file, "w") as config_file:
            json.dump(data_to_write, config_file)
    def recieve_request(self):
        """(blocking) recieve and parse an HTTP request"""
        conn, = self.sock.accept()
        request = conn.recv(1024)
        return self.parse_request(request)
    @staticmethod
    def parse_request(request):
        """
        Takes an HTTP request, returns an array
        containing requested dir and a dict of parameters
        """
        wanted = re.search(r"GET /(.*?)\ HTTP", request).group(1).strip().lower()
        wanted = str(wanted).replace("""%3a""", ":").replace("""%2f""", "/")
        params = {}
        if "?" in wanted:
            wanted = wanted.split("?")
            for i in range(1, len(wanted)): # first item will be requested dir
                tmp = wanted[i].split("=")
                if not "http://" in tmp[1] and not "https://" in tmp[1] and wanted[0] == "host":
                # maybe that's not neccesary
                    tmp[1] = "http://" + tmp[1]
                params[tmp[0]] =  tmp[1] # probably functionize this
            wanted = wanted[0]
        return [wanted, params]
    @staticmethod
    def send_page(conn, page):
        """Sends an HTTP response to conn containing page as it's content"""
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(page)
        conn.close()
        time.sleep(1)
