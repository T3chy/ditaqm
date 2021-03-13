"""
Class for interfacing with supported sensor modules
"""

from machine import SoftI2C, Pin, UART
import bme280
import bme680
import pms7003
import mics6814
import urequests as requests
POST_HEADERS = {'content-type': 'application/json'}
class Cluster:
    """
    Class for interfacing with supported sensor modules
    """
    def __init__(self, config):
        self.sensors = {}
        self.config = {}
        self.i2c = SoftI2C(Pin(5), Pin(4))
        # self.uart_1
        self.detect_sensors()
    def detect_sensors(self):
        """autodetects and initalizes sensors, returns a dict of detected sensors"""
        scan = self.i2c.scan()
        if len(scan) > 100:
            # scan returns every addr when sda is pulled up
            scan = []
        self.sensors = {}
        """
        Pin values for the MiCS6814 measurements
        """

        # attempt to detect bme sensors at their default i2c addresses
        if 118 in scan:
            self.sensors["bme280"] = bme280.BME280(i2c=self.i2c)
        if 117 in scan:
            self.sensors["bme680"] = bme680.BME680_I2C(i2c=self.i2c)

        # attempt to take a reading from the MiCS6814 sensor
        self.sensors["mics6814"] = mics6814.MICS6814()
        if self.sensors["mics6814"].read(detect=True) == 0: # nonsensical ADC value
            self.sensors.pop("mics6814") # not connected

        #attempt to initalize pms7003 sensor on uart bus 1
        try:
            pms = pms7003.PassivePms7003()
            self.sensors["pms7003"] = pms
        except pms7003.UartError:
            pass
        except TypeError:
            pass
        return list(self.sensors.keys())
    def take_measurement(self):
        """
        Take a measurement from connected sensors, returns a dict of all available data
        """
        full_sample = {}
        for sensor in self.sensors:
            tmp = {}
            try:
                tmp = self.sensors[sensor].read()
            except Exception as e:
                print('frig')
                print(e)
                pass # TODO make this useful
            full_sample.update(tmp)
        return full_sample
    def send_sample(self):
        """
        Sends a POST request to the provided host with all available data
        """
        body = self.take_measurement()
        body["sensorname"] = self.config["sensorname"]
        if "username" in self.config:
            body["username"] = self.config["username"]
        if "password" in self.config:
            body["password"] = self.config["password"]
        try:
            resp = requests.post(str(self.config["host"] + "/api/in"), headers=POST_HEADERS, data=body).json()
        except Exception as e:
            print("error POSTing data sample!")
            print(e)
            print('done printing error')
            return e
        return resp["code"]
