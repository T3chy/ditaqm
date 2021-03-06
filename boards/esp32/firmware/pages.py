"""Various HTML web pages used by firmware throughought setup and use"""
def choose_ssid(scanstr, retry=False):
    """The default page for the setup Access Point, takes list of ssids"""
    if retry:
        retry_string = "<h2>That didn't work :( please check your credentials and retry"
    else:
        retry_string = ""
    html_page = """<!DOCTYPE HTML>
        <html>
        <head>
          <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
            <body>
               <center>
                    <h2>Welcome to your Air Quality Cluster!</h2>
                    <h2>Please Select a SSID and enter a password to connect to a network!</h2>
                    """ + retry_string + """
                    <form>
                        """ + scanstr + """
                        <input id='pass' type='text' name="pass" placeholder="pass">
                        <input type="submit" value="Submit">
                    </form>
               </center>
           </body>
        </html>"""
    return html_page
def ssid_connect_success():
    """Page sent after successfully connecting to a WLAN network with supplied credentials"""
    html_page = """<!DOCTYPE HTML>
        <html>
        <head>
          <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
           <center><h2>Success! the device will now reboot. Connect (on the device you want to access the cluster from) to the wifi network you just entered the credentials for, and follow the instructions on the OLED!</h2></center>
           <center>
           </center>
           </body>
        </html>"""
    return html_page
def setup_home_page(host=0, uname=0, sname=0):
    """Homepage for sensor configuration"""
    if host:
        hosttext = """<b> done! your host is : """ + host + """</b>"""
    else:
        hosttext = """<a href= "/host"> do it! </a>"""
    if uname:
        logintext = """<b> done! Welcome, """ + uname  + """!</b>"""
    else:
        logintext = """<a href= "/login"> do it! </a>"""
    if sname:
        nametext = """<b> done! Your sensor name is """ + sname + """</b>"""
    else:
        nametext = """<a href= "/namesens"> do it! </a>"""
    html_page = """<!DOCTYPE HTML>
        <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body>
                <center>
                    <h2>Welcome to your Air Quality Cluster Setup!</h2>
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
def host_page(retry=False, hostentered=False):
    """Page to enter host to push data to"""
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
        if retry:
            retry_msg= """<h2> It appears that host doesn't exist :( please enter something like "https://albanylovestheair.com"</h2>"""
        else:
            retry_msg = ""
        html_page = """<!DOCTYPE HTML>
            <html>
                <head>
                  <meta name="viewport" content="width=device-width, initial-scale=1">
                </head>
                <body>
                   <center>
                       <h2>Welcome to your Air Quality Cluster Setup!</h2>
                       """ + retry_msg + """
                       <h2>Please enter your host below:</h2>
                   <form>
                       <input id='host' type='url' name="host" placeholder="https://yourwebsite.com">
                       <input type="submit" value="Submit">
                   </form> <br><br>
                   <a href="/"> return to home </a> </center>
                   </body>
            </html>"""

    return html_page

def name_sensor(retry=False, sensnamed=False, hostentered=False): #TODO page for when they haven't entered a host
    """Page to name sensor"""
    if hostentered:
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
            if retry:
                retry_msg= """<h2>It appears that your sensor name is not unique :( please enter something unique like [yourname]house</h2>"""
            else:
                retry_msg = ""
            html_page = """<!DOCTYPE HTML>
                <html>
                    <head>
                      <meta name="viewport" content="width=device-width, initial-scale=1">
                    </head>
                    <body>
                       <center>
                            <h2>Welcome to your Air Quality Cluster Setup!</h2>
                           """ + retry_msg + """
                           <h2>Please enter your chosen sensor name below:</h2>>
                           <form>
                               <input id='sensname' type='text' name="sensname" placeholder="ElamHouse">
                               <input type="submit" value="Submit">
                           </form> <br><br>
                           <a href="/"> return to homepage </a>
                       </center>
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
                    <a href="/"> return to home </a>
                </body>
            </html>"""
    return html_page



def login_page(hostentered=False, loggedin=False):
    """Page to login to user account"""
    if hostentered:
        if loggedin:
            html_page = """<!DOCTYPE HTML>
                <html>
                    <head>
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                    </head>
                    <body>
                        <center>
                            <h2>Welcome to your Air Quality Cluster Setup!</h2>
                            <h2>You are already logged in!
                            <form>
                                <input type="hidden" name="logout" value="1">
                                <input type="button" value=Log Out>?
                            </form> <br><br>
                            <a href="/"> return to home </a>
                            </h2>
                        </center>
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
                        <center>
                            <h2>Welcome to your Air Quality Cluster Setup!</h2>
                            <h2>Please enter your login credentials below:</h2>
                            <form>
                                <input id='uname' type='text' name="uname" placeholder="username">
                                <input id='pass' type='text' name="uname" placeholder="pass">
                                <input type="submit" value="Submit">
                            </form> <br><br>
                            <a href="/"> return to home </a>
                        </center>
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
                    <a href="/"> return to home </a>
                </body>
            </html>"""
    return html_page
