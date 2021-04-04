"""
Parent class used to assist in wireless setup
"""
import _thread
import json
import time
import re
import ssd1306
import usocket as socket
import network
from machine import Pin, SoftI2C
import status


class WebTool:
    """said parent class"""
    def __init__(self, config_lock=None, sample_lock= None, sock=None, config_file="config.json", np=False):
        sta = network.WLAN(network.STA_IF)
        if not sta.active():
            sta.active(True)
        while not sta.active():
            pass
        self.sta = sta
        self.ap = None
        self.ssid = None
        self.passwd = None
        self.config_file = config_file
        self.config_lock = config_lock
        self.sample_lock = sample_lock
        np = True
        self.status = status.Status(np=np)
        if sock:
            self.init_sock(sock)
        else:
            self.sock_bound = False
        self.i2c = SoftI2C(Pin(5), Pin(4))
        # check if ssd1306 (default addr 60 / 0x3c) is detected
        if 60 in self.i2c.scan():
            try:
                self.oled = ssd1306.SSD1306_I2C(128, 32, self.i2c)
            except Exception as e: # TODO make this specific
                print(e)
                self.oled = None
        else:
            self.oled = None
        try:
            with open(self.config_file):  # create config if it doesn"t exist
                pass
        except OSError:
            with open(self.config_file, "w") as config_descriptor:
                json.dump({},config_descriptor)
        # for DNS lookups
    def init_sock(self, sock):
        """Initalize a socket for interactive setup"""
        addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
        sock.bind(addr)
        sock.listen(1)
        self.sock_bound = True
        self.sock = sock

    def scan_ssids(self):
        """Scans local networks and returns an array of SSIDs"""
        return [net[0] for net in self.sta.scan()]
    def get_html_ssid_list(self):
        """Returns an HTML string containing dropdown menu with connectable SSIDs"""
        ssid_list = "<select id=\"ssid\" name=\"ssid\">"
        for ssid in self.scan_ssids():
            ssid = ssid.decode("utf-8")
            ssid = str(ssid).strip("b").strip("\"").strip("\"")
            ssid_list += "<option value= \"" + ssid + "\">" + ssid + "</option>"
        ssid_list +=  "</select>"
        return ssid_list

    def setup_ap(self, ssid="cluster"):
        """Sets up an Access Point and prints creds to OLED"""
        self.ssid = ssid
        ap = network.WLAN(network.AP_IF)
        ap.active(False)
        ap.active(True)
        ap.config(essid=ssid)
        while not ap.active():
            pass
        self.ap = ap

    def reset_oled(self):
        """Blank the optionally attached oled screen"""
        if self.oled:
            self.oled.fill(0)
            self.oled.show()
    def say(self, msg):
        """Print a given message to the optionally attached oled screen, 15 chars per line"""
        if self.oled:
            self.reset_oled()
            self.oled.text(str(msg[0:14]), 0, 0) # 1st line
            self.oled.text(str(msg[15:]), 0, 10) # 2nd line
            self.oled.show()
        print("printing \"" + str(msg) + "\" to oled")

    def wlan_is_connected(self): # should be a @property but it wasn"t working as on
        """Return if the device is connceted to WLAN"""
        try:
            return self.sta.isconnected()
        except AttributeError:
            return False
    @property
    def config(self):
        """return the config json file as a dictionary"""
        with open(self.config_file, "r") as config_file:
            config_data = json.load(config_file)
        return config_data

    def connect_to_wlan(self, ssid=None, passwd=None):
        """Attempt to connect to the given ssid with the given password, defaults to config"""
        if ssid and passwd:
            print("attempting to connect from given ssid(" + str(ssid) + ") and passwd (" + str(passwd) + ")")
            self.sta.connect(str(ssid), str(passwd))
        else:
            with open(self.config_file, "r") as config_file:
                config_data = json.load(config_file)
                if "ssid" in config_data and "passwd" in config_data:
                    self.sta.connect(str(config_data["ssid"]), str(config_data["passwd"]))
                else:
                    return 0
            self.say("connecting to  " + str(config_data["ssid"]))
        print('starting leds')
        self.status.inprogress.acquire()
        _thread.start_new_thread(self.status.connecting_seq, ())
        print("leds time")
        for _ in range(60):
            if self.sta.status() != network.STAT_CONNECTING:
                # break out on failure or success
                break
            time.sleep(1)
        print('canceling led coroutine')
        self.status.inprogress.release()
        if self.sta.isconnected():
            return self.sta.ifconfig()[0]
        print("failed to connect")
        print(str(self.sta.status()))
        return 0
    def write_config(self, data_to_write):
        """Updates the config file with key-values given in data_to_write"""
        with open(self.config_file, "r+") as config_file:
            config_data = json.load(config_file)
            for key in data_to_write:
                config_data[key] = data_to_write[key]
            config_file.seek(0)
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
        """
        (blocking) recieve and parse an HTTP request
        return parsed HTTP request and socket connection object
        """
        conn, _ = self.sock.accept()
        request = conn.recv(1024)
        parsed = self.parse_request(request)
        print("parsed request is " )
        print(parsed)
        return conn, parsed[0], parsed[1]
    @staticmethod
    def parse_request(request):
        """
        Takes an HTTP request, returns requested dir and a dict of parameters
        """
        if request == b"":
            return ["", {}]
        wanted = re.search(r"GET /(.*?)\ HTTP", request).group(1).strip()
        wanted = str(wanted, "utf-8").replace("""%3a""", ":").replace("""%2f""", "/")
        wanted = str(wanted, "utf-8").replace("""%3A""", ":").replace("""%2F""", "/")
        # I guess micropytthon doens"t have case insensitive subtitutions
        params = {}
        print("wanted =" + str(wanted))
        if "?" not in wanted:
            return [wanted, {}]
        wanted = wanted.split("?")
        wanted[0] = wanted[0].lower()
        wanted[1] = wanted[1].split("&")
        for i in range(len(wanted[1])):
            tmp = wanted[1][i].split("=")
            # if not "http://" in tmp[1] and not "https://" in tmp[1] and wanted[0] == "host":
            # # maybe this isn"t neccesary
            #     tmp[1] = "http://" + tmp[1]
            params[tmp[0]] = tmp[1]
        return [wanted[0], params]
    @staticmethod
    def send_page(conn, page):
        """Sends an HTTP response to conn containing page as it"s content"""
        try:
            conn.send("HTTP/1.1 200 OK\n")
            conn.send("Content-Type: text/html\n")
            conn.send("Connection: close\n\n")
            conn.sendall(page)
            conn.close()
            time.sleep(1)
        except OSError as e:
            print("error sending page")
            print(e)
            print("done printing error")
