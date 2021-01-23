from machine import I2C
from machine import Pin, I2C
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
scan = i2c.scan()
BME = 1
CJMCU = 1
if 118 in scan:
    print("BME sensor found!")
    BME = 0
if 72 in scan:
    print("CJMCU sensor found!")
    CJMCU = 0
with open("config", "a") as f:
    f.write(BME)
    f.write(CJMCU)
