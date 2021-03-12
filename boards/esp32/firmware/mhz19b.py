"""
class for measuring CO2 with the MH-Z19B sensor
"""
import time
from machine import Pin
import machine
class MHZ19B:
    def __init__(self, pwm_pin=21):
        self.pwm = Pin(pwm_pin)
    def read(self):
        """
        Take a CO2 level measurement, returns PPM
        """
        high_cycle_length = machine.time_pulse_us(self.pwm, 1)
        # time pusle us is negative for errors / no pulse
        return {"co2":5000*((high_cycle_length / 1000) -2) / (1000) if high_cycle_length > 0 else 0}
