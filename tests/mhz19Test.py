import pigpio # http://abyz.co.uk/rpi/pigpio/python.html
import read_PWM
import time

# Read the MH-Z19 CO2 sensor
PWM_GPIO = 4 # physical pin 7
var = 1
pi = pigpio.pi() # Grants access to Pi's GPIO
p = read_PWM.reader(pi, PWM_GPIO)

time.sleep(5)
try:
    pp = p.pulse_period()
    pw = p.pulse_width()
    if pp == 0.0 and pw == 0.0:
        var = 1
    else:
        var = 0
except:
    pass
print(var)
p.cancel()
pi.stop()
