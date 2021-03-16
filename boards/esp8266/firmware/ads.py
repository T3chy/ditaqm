# Copyleft Elam Day-Friedland 2021

# see https://cdn-shop.adafruit.com/datasheets/ads1115.pdf
# https://www.youtube.com/watch?v=4jcxeJxvi3Y
from machine import Pin, I2C
import time
i2c = I2C(scl=Pin(5), sda=Pin(4))
ADS_ADDR = 0x48

class ADS1115:
    def __init__(self, i2c):
        self.i2c = i2c
        # voltageConv = 6.114 / 325768.0 I think default gain (2.048v) is fine??
    def read(self):
        voltages = [0,0,0,0]
        ADSwrite = [0x00, 0x00, 0x00]
        voltageConv = 6.114 / 32768.0 # temp
        """iterate over the 4 analog inputs by writing to the config register and then reading"""
        for i in range(4):
            """Config Register Address"""
            ADSwrite[0] = 0x01
            """Config Register, 16 bits long"""
            """bit 15 = 1 (begin single conversion)"""
            """bits 11-9 = 000 (+/- 6.144V)""" # TODO maybe this could be lower
            """bit 8 = 1 (power-down single shot mode)"""
            if i == 0:
                """bits 14-12 = 100 (compare a0 and GND)"""
                ADSwrite[1] = 0xC1 # 11000001
            if i == 1:
                """bits 14-12 = 101 (compare a1 and GND)"""
                ADSwrite[1] = 0xD1 # 11010001
            if i == 2:
                """bits 14-12 = 110 (compare a2 and GND)"""
                ADSwrite[1] = 0xE1 # 11100001
            if i == 3:
                """bits 14-12 = 111 (compare a3 and GND)"""
                ADSwrite[1] = 0xF1 # 11110001
            """Second byte of config register; same for all AINs, basically just don't use the comparator"""
            """All defaults:
            bits 7-5 = 100 (128 samples per second)
            bit 4 = 0 (traditional comparator)
            bit 3 = 0 (active low comparator output)
            bit 2 = 0 (non-latching comparator)
            bits 1-0 = 11 (disable comparator)"""
            ADSwrite[2] = 0x83 # 10000011
            self.i2c.writeto(ADS_ADDR, bytes(ADSwrite)) #write 2 bytes to the config register
            """Conversion register address"""
            ADSwrite[0] = 0x00; # 00000000
            """Wait for conversion register to populate, 20ms is probably fine given sampling rate lmao"""
            time.sleep(.02)
            print(self.i2c.readfrom(ADS_ADDR, 2)) # conversion register is 2 bytes big
            """Gonna need to left shift first byte 8 bits left to stitch the values together""" #TODO do that
            reading = 0
            voltages[i] = reading * voltageConv
    def test(self):
        # self.i2c.write(bytes([0b1001000, 0b00000001, 0b11000101, 0b11100011]))
        self.i2c.writeto(ADS_ADDR, bytes([0b00000001, 0b11000101, 0b11100011]))
        time.sleep(.0013)
        self.i2c.writeto(ADS_ADDR, bytes([0b00000000]))
        print(self.i2c.readfrom(ADS_ADDR,2))
    def write(self):
        pass # TODO write this lmao
