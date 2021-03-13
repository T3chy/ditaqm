# needs 20 mins to warm up before sensor readings are usable
from machine import ADC, Pin
import time
import math

ADC_MAX_VALUE = 4095
ADC_MIN_VALUE = 0
ADC_SAMPLE = 3
ADC_SAMPLE_DELAY = 100
# ask ajith about these
V0_CH0 = 0.24988262581255533
V0_CH1 = 1.712802270577105
V0_CH2 = 2.786960051271096
R00 = 69./((3.3/V0_CH0)-1.)
R01 = 220./((3.3/V0_CH0)-1.)
R02 = 220./((3.3/V0_CH0)-1.)
R00 = 48.
R01 = 29.
R02 = 160.
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
            ch0_voltage = self.no2.read() * (3.3/4095)
            ch1_voltage = self.nh3.read() * (3.3/4095)
            ch2_voltage = self.co.read() * (3.3/4095)
            if ch0_voltage == 0 and ch1_voltage == 0 and ch2_voltage == 0:
                sane = False
                break
            ch0_oxy_r =  69./((3.3/ch0_voltage)-1.)
            ch1_nh3_r =  220./((3.3/ch1_voltage)-1.)
            ch2_red_r =  220./((3.3/ch2_voltage)-1.)

            ch0_oxy_r_ratio = ch0_oxy_r/R00
            ch1_nh3_r_ratio = ch1_nh3_r/R01
            ch2_red_r_ratio = ch2_red_r/R02

            tmpno2 =+ 0.1516*math.pow(ch0_oxy_r_ratio, 0.9979)
            tmpnh3 =+ 0.6151*math.pow(ch1_nh3_r_ratio, -1.903)
            tmpco =+ 4.4638*math.pow(ch2_red_r_ratio, -1.177)
            if not tmpno2 or not tmpnh3 or not tmpco:
                sane = False
            time.sleep_ms(ADC_SAMPLE_DELAY)
        if sane:
            return {"no2":tmpno2 / ADC_SAMPLE, "nh3":tmpnh3 / ADC_SAMPLE, "co": tmpco / ADC_SAMPLE}
        return 0
