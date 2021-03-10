"""
An inital access Point generated when there are no WAN network credentials configured
"""
import machine
import time
import pages
From webtool import WebTool

class SetupAp(WebTool):
    """Help the user connect to an SSID"""
    def __init__(self):
        super().__init__()
        super().connect_to_wlan()
    def run(self, sock):
        """Serve HTTP with connection options, try to connect to WLAN, repeat"""
        super().init_sock(sock)
        ssid_html = super().get_html_ssid_list()
        super().setup_ap()
        conn_succ = False
        while True:
            if super().wlan_is_connected():
                break
            conn , _ , params = super().recieve_request() # wanted dir doesn't matter here
            if "ssid" in params:
                if "pass" not in params: # might not be necessary
                    params["pass"] = ""
                conn_succ = super().connect_to_wlan(ssid=params["ssid"], passwd=params["pass"])
                if conn_succ:
                    to_send = pages.ssid_connect_success()
                    super().say("connected!")
                    super().write_config({"ssid": params["ssid"], "passwd":params["pass"]})
                else:
                    to_send = pages.choose_ssid(ssid_html, retry=True)
            else:
                to_send = pages.choose_ssid(ssid_html)
            super().send_page(conn, to_send)
