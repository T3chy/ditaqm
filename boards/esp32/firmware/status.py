import machine, neopixel
import time
import _thread


class Status:
    """
    Status LED stuff, uses the 2 onboard LEDs and a neopixel if it's there
    """
    def __init__(self, np_pin=22, np=False, n_neopixels=8):
        # defaults to the RX1 header as the control pin, change this if you want
        if np:
            self.np = neopixel.NeoPixel(machine.Pin(np_pin), n_neopixels)
            self.n_neopixels = n_neopixels
        self.green = machine.Pin(18, machine.Pin.OUT)
        self.blue = machine.Pin(19, machine.Pin.OUT)
        self.inprogress = _thread.allocate_lock()
    def change_onboard(self, green=False, blue=False):
        """
        change the status of the two onboard LEDs
        """
        if green:
            self.green.value(1)
        else:
            self.green.value(0)
        if blue:
            self.blue.value(1)
        else:
            self.blue.value(0)
    def set_all_neopixels(self, val=[(0,0,0,0)]):
        """Blank all attached neopixels"""
        if len(val) == 1:
            for np_idx in range(self.n_neopixels):
                self.np[np_idx] = val[0]
        for np_idx in range(self.n_neopixels):
            self.np[np_idx] = val[np_idx]
        self.np.write()
    def connecting_seq(self):
        """
        blink the blue led and wave the neopixel stick, indicates connecting to wifi
        """
        print('connecting seq called')
        tick = True
        while self.inprogress.locked():
            print('led coroutine time')
            self.change_onboard(blue=True)
            self.set_all_neopixels()
            if tick:
                for np_idx in range(self.n_neopixels):
                    self.np[np_idx] = (0, 0, 20, 0)
                    if np_idx > 0:
                        self.np[np_idx - 1] = (0,0,0,0)
                    self.np.write()
                    time.sleep(.1)
                    self.change_onboard()
                tick = False
            else:
                for np_idx in reversed(range(self.n_neopixels)):
                    self.np[np_idx] = (0, 0, 20, 0)
                    if np_idx != self.n_neopixels - 1:
                        self.np[np_idx + 1] = (0,0,0,0)
                    self.np.write()
                    time.sleep(.1)
                tick= True
        self.set_all_neopixels()
        self.set_all_neopixels(val=(0,20,0,0))
        time.sleep(.25)
        self.set_all_neopixels()
