from machine import I2C
import json
from machine import Pin, I2C
def update_config():
    i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
    scan = i2c.scan()
    CONFIG = ""
    try:
        # initalize sensors, host, name from config file
        with open("config.json", "r") as f:
            CONFIG = json.loads(f)
            USERNAME = CONFIG["username"]
            PASSWORD = CONFIG["password"]
            HOST = CONFIG["host"]
            SENSOR_NAME = CONFIG["sensorname"]
            BME = int(CONFIG["BME"])
            CJMCU = int(CONFIG["CJMCU"])
            MHZ19B = int(CONFIG["MHZ19B"])
    except IOError as error: # config file probably not created if this fails
        print(error)

    if 118 in scan:
        print("BME sensor found!")
        CONFIG["BME"] = 1
    else:
        CONFIG["BME"] = 0
    if 72 in scan:
        print("CJMCU sensor found!")
        CONFIG["CJMCU"] = 1
    else:
        CONFIG["CJMCU"] = 0

    try:
        with open("config.json", "w") as f:
            f.write(BME)
            f.write(CJMCU)
    except IOError as error:
        print(error)
