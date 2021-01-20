#!/usr/bin/python3
"""Periodically send bme280 data via POST request to a designated host"""
import sys
import time
import board
import requests
from busio import I2C
import adafruit_bme280
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import math
import pigpio
sys.path.append("tests/")
import read_PWM

# constants
R00 = 48.
R01 = 29.
R02 = 160.

PWM_GPIO = 4
# Create library object using our Bus I2C port
try:
    config = open("config", "r")
    host = config.readline().strip("\n") + "/in"
    name = config.readline().strip("\n")
    bme = config.readline().strip("\n")
    cjmcu = config.readline().strip("\n")
    mhz19b = config.readline().strip("\n")
except Exception as e:
    print(e)

if bme:
    try:
        i2c = I2C(board.SCL, board.SDA)
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
        val = 0
    except:
        try:
            i2c = I2C(board.SCL, board.SDA)
            bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
        except:
            print(1)
    bme280.sea_level_pressure = 1013.25
if cjmcu:
    try:
        # Create the I2C bus
        i2c = busio.I2C(board.SCL, board.SDA)

        # Create the ADC object using the I2C bus
        ads = ADS.ADS1115(i2c) # default addr; 48

        # Create single-ended input on channels 0-2
        chan0 = AnalogIn(ads, ADS.P0)
        chan1 = AnalogIn(ads, ADS.P1)
        chan2 = AnalogIn(ads, ADS.P2)
    except:
        print(1)


def update():
    """gather data for connected sensors and return dictionary with it for POSTing"""
    res = {}
    if bme:
        res["temp"] = bme280.temperature
        res["humidity"] = bme280.humidity
        res["pressure"] = bme280.pressure
        res["altitude"] = bme280.altitude
    if cjmcu:
        ch0_oxy_R =  69./((5.0/chan0.voltage)-1.)
        ch1_nh3_R =  220./((5.0/chan1.voltage)-1.)
        ch2_red_R =  220./((5.0/chan2.voltage)-1.)

        ch0_oxy_Rratio = ch0_oxy_R/R00
        ch1_nh3_Rratio = ch1_nh3_R/R01
        ch2_red_Rratio = ch2_red_R/R02

        res["NO2"] = 0.1516*math.pow(ch0_oxy_Rratio, 0.9979)
        res["NH3"] = 0.6151*math.pow(ch1_nh3_Rratio, -1.903)
        res["CO"] = 4.4638*math.pow(ch2_red_Rratio, -1.177)
    if mhz19b:
        pi = pigpio.pi()
        p = read_PWM.reader(pi, PWM_GPIO)
        time.sleep(5)
        pp = p.pulse_period()
        pw = p.pulse_width()
        res["CO2"] = (5000.0)*(pw-2.0)/(pp-4.0)
    return res

if len(sys.argv) == 2:
    try:
        print(requests.post(host, data=update()))
    except Exception as e:
        print(e)
else:
    while True:
        try:
            print(requests.post(host, data=update()))
        except Exception as e:
            print(e)
        time.sleep(55)
