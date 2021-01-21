#!/usr/bin/python3
"""Test if a MH-Z19 CO2 sensor is connected"""
import pigpio # http://abyz.co.uk/rpi/pigpio/python.html
import read_PWM
import time

# Read the MH-Z19 CO2 sensor
PWM_GPIO = 4 # physical pin 7

CODE = 0
pi = pigpio.pi() # Grants access to Pi's GPIO
pulse = read_PWM.reader(pi, PWM_GPIO)

time.sleep(5)
try: #TODO maybe do reasonable value checking?
    pulse_width = pulse.pulse_period()
    pulse_width = pulse.pulse_width()
    if pulse_width == 0.0 and pulse_width == 0.0:
        CODE = 1
except:
    pass
print(CODE)
pulse.cancel()
pi.stop()
