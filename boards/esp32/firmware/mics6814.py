# needs 20 mins to warm up before sensor readings are usable
from machine import ADC, Pin
import time

ADC_MAX_VALUE = 4095
ADC_MIN_VALUE = 0
ADC_SAMPLE = 3
ADC_SAMPLE_DELAY = 100
class MICS6814:
    """Class for interacting with the MiCS-6814 sensor"""
    def __init__(self, no2_pin=Pin(33), nh3_pin=Pin(32), co_pin=Pin(34)):
        """Takes in Pin object for each line and creates ADC objects"""
        self.no2 = ADC(no2_pin)
        self.nh3 = ADC(nh3_pin)
        self.co = ADC(co_pin)
        for pin in [self.no2, self.nh3, self.co]:
            pin.atten(ADC.ATTN_11DB)
        """
        According to datasheet, the MiCS-6814 outputs a max of 2.4v on the analog pins so we attenuate to 11db where the max input voltage is 3.6v to be safe
        """
    def read(self):
        """returns a dictionary containing measurements after taking ADC_SAMPLE samples"""
        sane = True
        tmpno2 = 0
        tmpnh3 =  0
        tmpco = 0
        for _ in range(ADC_SAMPLE):
            tmp = self.no2.read()
            if ADC_MIN_VALUE  >= tmp <= ADC_MAX_VALUE:
                tmpno2 += tmp
            else:
                sane = False
            tmp = self.nh3.read()
            if ADC_MIN_VALUE  >= tmp <= ADC_MAX_VALUE:
                tmpnh3 += tmp
            else:
                sane = False
            tmp = self.co.read()
            if ADC_MIN_VALUE  >= tmp <= ADC_MAX_VALUE:
                tmpco += tmp
            else:
                sane = False
            time.sleep_ms(ADC_SAMPLE_DELAY)
        if sane:
            return {"no2":tmpno2 / ADC_SAMPLE, "nh3":tmpnh3 / ADC_SAMPLE, "co": tmpco / ADC_SAMPLE}
        return 0
