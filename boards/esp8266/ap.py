import machine
import time
import re
import json


# ************************
# Configure the ESP32 wifi
# as Access Point mode.
import network
ssid = 'Your Air Quality Cluster!'
passwd = '123456789'

sta = network.WLAN(network.STA_IF)
sta.active(True)
while not sta.active():
    pass
scan = [net[0] for net in sta.scan()]
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=passwd)
while not ap.active():
    pass
print('network config:', ap.ifconfig())
scanstr = "<select id=\"ssid\" name=\"ssid\">"
for ssid in scan:
    ssid = str(ssid).strip('b').strip('\'').strip("\"")
    scanstr = scanstr + "<option value= \"" + ssid + "\">" + ssid + "</option>"
scanstr = scanstr + "</select>"


# ************************
# Configure the socket connection
# over TCP/IP
import socket

# AF_INET - use Internet Protocol v4 addresses
# SOCK_STREAM means that it is a TCP socket.
# SOCK_DGRAM means that it is a UDP socket.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',80)) # specifies that the socket is reachable by any address the machine happens to have
s.listen(5)     # max of 5 socket connections

# ************************
# Function for creating the
# web page to be displayed
def web_page():
    html_page = """<!DOCTYPE HTML>
        <html>
        <head>
          <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
           <center><h2>Welcome to your Air Quality Cluster!</h2></center>
           <center><h2>Please Select a SSID and enter a password to connect to a network!</h2></center>
           <center>
             <form>
                """ + scanstr + """
               <input id='pass' type='text' name="pass" placeholder="pass">
               <input type="submit" value="Submit">
             </form>
           </center>
           </body>
        </html>"""
    return html_page
def success():
    html_page = """<!DOCTYPE HTML>
        <html>
        <head>
          <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
           <center><h2>success! Connect (on the device you want to access the cluster from) to the wifi network you just entered the credentials for, and follow the instructions on the OLED!</h2></center>
           <center>
           </center>
           </body>
        </html>"""
    return html_page

flag = 0
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
                    continue
            if sta.isconnected():
                flag = 1
        except Exception as e:
            print(e)
except:
    pass

if not flag:
    print('serving')
    while True:
        conn, addr = s.accept()
        request=conn.recv(1024)
        # print("Content %s" % str(request))
        ssid = None
        passwd = None
        request = str(request, 'utf8')
        if "GET /?ssid=" in request:
            print('ssid request time')
            try:
                ssid = re.search(r"ssid=(.*?)\&", request).group(1).strip()
                passwd = re.search(r"pass=(.*?)\ HTTP", request).group(1).strip()
                if ssid and passwd:
                    print("ssid:", ssid)
                    print("pass:", passwd)
                    sta.connect(str(ssid), str(passwd))
                    counter = 0
                    while not sta.isconnected():
                        time.sleep(1)
                        counter += 1
                        if counter > 5:
                            continue
                    print("connected! " + str(sta.ifconfig()))
                    response = success()
                    conn.send('HTTP/1.1 200 OK\n')
                    conn.send('Content-Type: text/html\n')
                    conn.send('Connection: close\n\n')
                    conn.sendall(response)
                    conn.close()
                    time.sleep(1)
                    ap.active(False)
                    break
            except Exception as e:
                print(e)

        # Socket send()
        response = web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()
    with open("config.json", "w") as f:
        try:
            data = json.load(f)
        except:
            data = {}
        data["ssid"] = ssid
        data["passwd"] = passwd
        json.dump(data, f)
else:
    ap.active(False)
    print('alreadfy conncetd')
s.close()
