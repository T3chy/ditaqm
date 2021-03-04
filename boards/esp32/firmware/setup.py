# TODO check unique first and then register sens
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
s.bind(('',80)) # specifies that the socket is reachable by any address the machine happens to have
s.listen(5)     # max of 5 socket connections

# ************************
# Function for creating the
# web page to be displayed

dns_addr = socket.getaddrinfo("127.0.0.1", 53)[0][-1]

POST_HEADERS = """\
POST {rdir} HTTP/1.1\r
Content-Type: {content_type}\r
Content-Length: {content_length}\r
Host: {host}\r
Connection: close\r
\r\n"""


def print_config():
    with open("config.json", "r") as f:
        print("printing config")
        for line in f:
            print(line)
        print('done printing config')
        f.seek(0)

def reset_settings():
    print("resetting setings")
    print_config()
    hostentered = False
    loggedin = False
    sensnamed = False

    HOST= "NA"
    UNAME = "NA"
    SNAME = "NA"
    with open('config.json', 'r') as f:
        content = json.load(f)
    with open('config.json', 'w') as f: # erase file , truncate doesn't seem to work
        content.pop('host', None)
        content.pop('sensname', None)
        content.pop('username', None)
        content.pop('password', None)
        f.seek(0)
        json.dump(content,f)
    print('settings reset')
    print_config()


def dict_to_body(data):
    body = ""
    for key in data:
        body = body + str(key) + "=" + str(data[key]) + "&"
    return body
def send(host,  dict_to_send, rdir="/", PORT=80):
    # try:
    body = dict_to_body(dict_to_send)
    body_bytes = body.encode('ascii')

    addrinfo = socket.getaddrinfo(host, PORT)[0][-1]
    header_bytes = POST_HEADERS.format(
        content_type="application/x-www-form-urlencoded",
        content_length=len(body_bytes),
        rdir = rdir,
        host=str(addrinfo[0]) + ":" + str(PORT)
    ).encode('iso-8859-1')

    payload = header_bytes + body_bytes

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addrinfo = socket.getaddrinfo(host, PORT)[0][-1]
    s.connect((addrinfo[0], addrinfo[1]))

    s.sendall(payload)

    return s.recv(1024)
    # except Exception as e:
    #     print("bruh" + str(e))
    #     return -1

def main_page():
    if hostentered:
        hosttext = """<b> done! your host is : """ + HOST + """</b>"""
    else:
        hosttext = """<a href= "/host"> do it! </a>"""
    if loggedin:
        logintext = """<b> done! Welcome, """ + UNAME  + """!</b>"""
    else:
        logintext = """<a href= "/login"> do it! </a>"""
    if sensnamed:
        nametext = """<b> done! Your sensor name is """ + SNAME + """</b>"""
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
                   <li> (optional) Login / Register an Account: : """ + logintext + """ </li>
                   <li> Name your sensor: """ + nametext + """ </li>
               </ol>
               <a href="/reset"> reset settings </a>
           </center>
           </body>
        </html>"""
    return html_page
def host_page(retry=False):
    if hostentered:
        html_page = """<!DOCTYPE HTML>
            <html>
            <head>
              <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body>
               <center><h2>Welcome to your Air Quality Cluster Setup!</h2></center>
               <center><h2>You have already selected a host!
               <form>
                   <input type="hidden" name="reset host" value="1">
                   <input type="button" value=Reset Host>?
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
               <center><h2>Welcome to your Air Quality Cluster Setup!</h2>
               """ + ("""<h2> It appears that host doesn't exist :( please enter something like "https://albanylovestheair.com"</h2>"""if retry else "") + """
               <center><h2>Please enter your host below:</h2></center>
               <form>
                   <input id='host' type='url' name="host" placeholder="https://yourwebsite.com">
                   <input type="submit" value="Submit">
               </form><br><br>
               <a href="/"> return to home </a> </center>
               </body>
            </html>"""
    return html_page
def sensname_page(retry=False):
    pass
    if sensnamed:
        html_page = """<!DOCTYPE HTML>
            <html>
            <head>
              <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body>
               <center><h2>Welcome to your Air Quality Cluster Setup!</h2></center>
               <center><h2>You have already named your sensor!!
               <form>
                   <input type="hidden" name="reset host" value="1">
                   <input type="button" value=Reset Host>?
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
               <center><h2>Welcome to your Air Quality Cluster Setup!</h2>
               """ + ("""<h2> It appears that your sensor name is not unique :( please enter something unique like [yourname]house</h2>"""if retry else "") + """
               <center><h2>Please enter your chosen sensor name below:</h2></center>
               <form>
                   <input id='sensname' type='text' name="sensname" placeholder="ElamHouse">
                   <input type="submit" value="Submit">
               </form><br><br>
               <a href="/"> return to home </a> </center>
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
               <center><h2>Please <a href="../host"> enter a host </a> first! </h2></center>
            </body>
           <br><br>
           <a href="/"> return to home </a>
            </html>"""
    return html_page


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
    conn, addr = s.accept()
    request=conn.recv(1024)
    request = str(request, 'utf8')
    if request != "":
        wanted = re.search(r"GET /(.*?)\ HTTP", request).group(1).strip().lower()
        wanted = str(wanted).replace("""%3a""", ":").replace("""%2f""", "/")
        args = {}
        if "?" in wanted:
            wanted = wanted.split("?")
            for i in range(1, len(wanted)):
                tmp = wanted[i].split("=")
                if not "http://" in tmp[1] and not "https://" in tmp[1] and "host" == wanted[0]:
                    tmp[1] = "http://" + tmp[1]
                args[tmp[0]] =  tmp[1] # probably functionize this
            wanted = wanted[0]
        response = main_page()
        if wanted == "login":
            response = login_page()
        elif wanted == "host":
            print(wanted)
            print("args: " + str(args))
            if "host" in args:
                print(args['host'])
                try:
                    resp = requests.get(str(args["host"] + "/test")).text
                except Exception as e:
                    print(e)
                    print(resp)
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
                    print("host is: " + str(HOST))
                    resp = requests.post(str(HOST + "/api/checkUnique"), data=uname).text
                    print(resp)
                except Exception as e:
                    print(e)
                    resp = 0
                if resp == "OK":
                    try:
                        uname = json.dumps({"name":args['sensname']})
                        resp = requests.get(str(HOST + "/api/regSens")).text
                        with open('config.json', 'r+') as f:
                            content = json.load(f)
                            content["sensname"] = args["sensname"]
                            f.seek(0)
                            json.dump(content,f)
                            print("sensor name added to configuration!")
                        sensnamed = True
                        SNAME = args["sensname"]
                        response = main_page()
                    except Exception as e:
                        print(e)
                        print(resp)
                else:
                    response = sensname_page(retry=True)
            else:
                response = sensname_page(retry=False)

        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()
    else:
        pass
