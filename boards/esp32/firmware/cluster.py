"""
Class for interfacing with supported sensor modules
"""

from machine import SoftI2C, Pin
import bme280
import bme680
import mics6814
class Cluster:
    """
    Class for interfacing with supported sensor modules
    """
    def __init__(self):
        self.sensors = {}
        self.detect_sensors()
        self.i2c = SoftI2C(Pin(5), Pin(4))
    def detect_sensors(self):
        """autodetects and initalizes sensors, returns an array of detected sensors"""
        scan = self.i2c.scan()
        """
        Pin values for the MiCS6814 measurements
        """
        if 118 in scan:
            self.sensors["bme280"] = bme280.BME280(i2c=self.i2c)
        if 117 in scan:
            self.sensors["bme680"] = bme680.BME680_I2C(i2c=self.i2c)
        self.sensors["mics6814"] = mics6814.MICS6814()
        if self.sensors["mics6814"].read() == 0: # nonsensical ADC value
            self.sensors.pop("mics6814") # not connected
        return self.sensors.keys()
    def take_measurement(self):
        pass
