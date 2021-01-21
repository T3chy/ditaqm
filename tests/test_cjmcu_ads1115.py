#!/usr/bin/python3
"""Test the MiCS-6814 onness via ads1115 by attempting to initalize it, returns 0 on success and 1 on failure"""

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


CODE = 1
try: # TODO do reasonable value checking?
    # Create the I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)

    # Create the ADC object using the I2C bus
    ads = ADS.ADS1115(i2c) # default addr; 48

    # Create single-ended input on channels 0-2
    chan0 = AnalogIn(ads, ADS.P0)
    chan1 = AnalogIn(ads, ADS.P1)
    chan2 = AnalogIn(ads, ADS.P2)
    CODE = 0
except IOError:
    pass
except ValueError:
    pass
except Exception as e:
    print(e)
print(CODE)
