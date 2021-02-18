import machine
from machine import Pin, I2C
import time
import re
import json
import socket


# ************************
# Configure the ESP32 wifi
# as Access Point mode.
import network

sta = network.WLAN(network.STA_IF)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sta.active(False)
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
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',80)) # specifies that the socket is reachable by any address the machine happens to have
s.listen(5)     # max of 5 socket connections

# ************************
# Function for creating the
# web page to be displayed
hostentered = False
loggedin = False
sensnamed = False

host = "NA"
uname = "NA"
sname = "NA"

POST_HEADERS = """\
POST /in HTTP/1.1\r
Content-Type: {content_type}\r
Content-Length: {content_length}\r
Host: {host}\r
Connection: close\r
\r\n"""

def check_host(host):
        body = dict_to_body(update())
        body_bytes = body.encode('ascii')
        header_bytes = HEADERS.format(
        content_type="application/x-www-form-urlencoded",
        content_length=len(body_bytes),
        host=str(HOST) + ":" + str(PORT)
    ).encode('iso-8859-1')

def main_page():
    if hostentered:
        hosttext = """<b> done! your host: """ + host + """</b>"""
    else:
        hosttext = """<a href= "/host"> do it! </a>"""
    if loggedin:
        logintext = """<b> done! Welcome, """ + uname + """!</b>"""
    else:
        logintext = """<a href= "/login"> do it! </a>"""
    if sensnamed:
        nametext = """<b> done! Your sensor name is """ + sname + """</b>"""
    else:
        nametext = """<a href= "/namesens"> do it! </a>"""
    html_page = """<!DOCTYPE HTML>
        <html>
        <head>
          <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
           <center><h2>Welcome to your Air Quality Cluster Setup!</h2></center>
           <center>
               <ol>
                   <li> Enter your host (website): """ + hosttext + """ </li>
                   <li> Login / Register an Account: : """ + logintext + """ </li>
                   <li> Name your sensor: """ + nametext + """ </li>
               </ol>
           </center>
           </body>
        </html>"""
    return html_page
def login_page():
    if hostentered:
        if loggedin:
            html_page = """<!DOCTYPE HTML>
                <html>
                <head>
                  <meta name="viewport" content="width=device-width, initial-scale=1">
                </head>
                <body>
                   <center><h2>Welcome to your Air Quality Cluster Setup!</h2></center>
                   <center><h2>You are already logged in!
                   <form>
                       <input type="hidden" name="logout" value="1">
                       <input type="button" value=Log Out>?
                   </form><br><br>
                   <a href="/"> return to home </a>
                   </h2></center>
                </body>
                </html>
            """

        else:
            html_page = """<!DOCTYPE HTML>
                <html>
                <head>
                  <meta name="viewport" content="width=device-width, initial-scale=1">
                </head>
                <body>
                   <center><h2>Welcome to your Air Quality Cluster Setup!</h2></center>
                   <center><h2>Please enter your login credentials below:</h2></center>
                   <form>
                       <input id='uname' type='text' name="uname" placeholder="username">
                       <input id='pass' type='text' name="uname" placeholder="pass">
                       <input type="submit" value="Submit">
                   </form><br><br>
                   <a href="/"> return to home </a>
                   </body>
                </html>"""
    else:
        html_page = """<!DOCTYPE HTML>
            <html>
            <head>
              <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body>
               <center><h2>Please <a href="../hostinit"> enter a host </a> first! </h2></center>
            </body>
           <br><br>
           <a href="/"> return to home </a>
            </html>"""
    return html_page
def host_page():
    pass


print('serving')
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
    machine.reset()
if not flag:
    machine.reset()

while True:
    conn, addr = s.accept()
    request=conn.recv(1024)
    print(request)
    request = str(request, 'utf8')
    wanted = re.search(r"GET /(.*?)\ HTTP", request).group(1).strip().lower()
    if wanted == "login":
        response = login_page()
    else:
        response = main_page()

    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
