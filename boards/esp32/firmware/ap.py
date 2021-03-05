"""
An inital access Point generated when there are no WAN network credentials configured
"""
import pages
from webtool import WebTool

class SetupAp(WebTool):
    """Help the user connect to an SSID"""
    def __init__(self, sock):
        super().__init__(sock)
        self.ssid_html = super().get_html_ssid_list()
        super().setup_ap()
    def run(self):
        """Serve HTTP with connection options, try to connect to WLAN, repeat"""
        conn_succ = False
        while True:
            conn , dirr, params = super().recieve_request() # wanted dir doesn't matter here
            if "ssid" in params:
                if "pass" not in params: # might not be necessary
                    params["pass"] = ""
                conn_succ = super().connect_to_wlan(ssid=params["ssid"], passwd=params["pass"])
                if conn_succ:
                    to_send = pages.ssid_connect_success()
                    super().say("connected!")
                    super().write_config({"ssid": params["ssid"], "pass":params["pass"]})
                else:
                    to_send = pages.choose_ssid(self.ssid_html, retry=True)
            else:
                to_send = pages.choose_ssid(self.ssid_html)
            super().send_page(conn, to_send)
            if conn_succ:
                self.sock.close()
                break
