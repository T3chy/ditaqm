"""
class for measuring CO2 with the MH-Z19B sensor
"""
import time
from machine import Pin
import machine
class MHZ19B:
    def __init__(self, pwm_pin=14):
        self.pwm = Pin(pwm_pin)
    def measure(self):
        """
        Take a CO2 level measurement
        """
        high_cycle_length = machine.time_pulse_us(self.pwm, 1)
        return (2000*(high_cycle_length) / (1000)) if high_cycle_length > 0 else 0

#             # send a read command to the sensor
#             self.uart.write(b'\xff\x01\x86\x00\x00\x00\x00\x00\x79')
#             # wait for the sensor to measure and send dataa
#             time.sleep(1)

#             # read / validate data
#             buf = self.uart.read(9)
#             if self.is_valid(buf):
#                 break

#             # retry if data isn't valid
#             print("invalid mh-z19b data: ")
#             print(buf)
#             print('retrying...')
#             co2 = buf[2] * 256 + buf[3]
#             print('co2         = %.2f' % co2)
#             return co2

#     @staticmethod
#     def is_valid(buf):
#         """
#         Verifies data validitiy with checksum algorithm from datasheet
#         """
#         if buf is None or buf[0] != 0xFF or buf[1] != 0x86:
#             return False
#         i = 1
#         checksum = 0x00
#         while i < 8:
#             checksum += buf[i] % 256
#             i += 1
#         checksum = ~checksum & 0xFF
#         checksum += 1
#         return checksum == buf[8]
#     def read_pwm(self):
#         pass
#         """ Utilizes PWM to read CO2 Level """
