#!/usr/bin/python3
"""Test the BME280 Sensor by attempting to initalize it at the two i2c addresses it appears at, returning 0 on success and 1 on failure"""

import board
from busio import I2C
import adafruit_bme280

CODE = 0


try:
    i2c = I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    bme280.sea_level_pressure = 1013.25
except ValueError:
    try:
        i2c = I2C(board.SCL, board.SDA)
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
        bme280.sea_level_pressure = 1013.25
    except ValueError:
        CODE = 1
except IOError:
    CODE = 1
except Exception as e:
    print(e)
print(CODE)
