#!/usr/bin/python3
"""Test if a MH-Z19b CO2 sensor is connected by reading the pwm signal of physical pin 7"""

import time
import pigpio # http://abyz.co.uk/rpi/pigpio/python.html
import read_pwm

# Read the MH-Z19 CO2 sensor
PWM_GPIO = 4 # physical pin 7

CODE = 0
pi = pigpio.pi() # Grants access to Pi's GPIO
pulse = read_pwm.PwmReader(pi, PWM_GPIO)

time.sleep(5)
try: #TODO maybe do reasonable value checking?
    pulse_width = pulse.pulse_period()
    pulse_width = pulse.pulse_width()
    if pulse_width == 0.0 and pulse_width == 0.0:
        CODE = 1
except: # no idea what error this might be
    pass
print(CODE)
pulse.cancel()
pi.stop()
