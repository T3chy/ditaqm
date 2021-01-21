#!/usr/bin/python3
"""Test the BME280 Sensor"""

import board
from busio import I2C
import adafruit_bme280
CODE = 0
try:
    i2c = I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    bme280.sea_level_pressure = 1013.25
except:
    try:
        i2c = I2C(board.SCL, board.SDA)
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
        bme280.sea_level_pressure = 1013.25
    except:
        CODE = 1
print(CODE)
