#!/usr/bin/ python3

# read_pwm.py (Modified by E. Day on 1/21/2021)
# 2015-12-08
# Public Domain

import pigpio # http://abyz.co.uk/rpi/pigpio/python.html

class PwmReader:
    """
    A class to read PWM pulses and calculate their frequency
    and duty cycle.  The frequency is how often the pulse
    happens per second.  The duty cycle is the percentage of
    pulse high time per cycle.
    Class "reader" has no common attributes.  Only instant attributes
    as described below (use of self is important).
    """

    def __init__(self, pi, gpio):
        """
        Instantiate with the Pi and gpio of the PWM signal
        to monitor.
        """
        self.pi = pi
        self.gpio = gpio

        self._high_tick = None
        self._period = None
        self._high = None

        pi.set_mode(gpio, pigpio.INPUT) # Sets the mode of gpio pin

        """
        Calls a user supplied function (a callback) whenever the specified
        GPIO edge is detected.
        callback(user_gpio, edge, func)
        user_gpio = 0-31
        edge = EITHER_EDGE, RISING_EDGE (default), or FALLING_EDGE.
        func = user supplied callback function. _cbf here.
        """

        self._cb = pi.callback(gpio, pigpio.EITHER_EDGE, self._cbf)

        """
        The user supplied callback receives three parameters:
        the GPIO, the level, and the tick.
        Parameter   Value    Meaning
        GPIO        0-31     The GPIO which has changed state
        level       0-2      0 = change to low (a falling edge)
                             1 = change to high (a rising edge)
                             2 = no level change (a watchdog timeout)
        tick        32 bit   The number of microseconds since boot
                             WARNING: this wraps around from
                            4294967295 to 0 roughly every 72 minutes
        """

    def _cbf(self, gpio, level, tick):

        if level == 1: # Change to high

            if self._high_tick is not None:

                """
                pigpio.tickDiff(t1,t2) returns the microsesecond difference
                between two ticks.
                Automatically takes care of the tick reset after
                roughly every 72 mins (when the 32 bit register overflows).
                """
                tick_diff = pigpio.tickDiff(self._high_tick, tick)
                self._period = tick_diff

            self._high_tick = tick

        elif level == 0: # Change to low

            if self._high_tick is not None:
                tick_diff = pigpio.tickDiff(self._high_tick, tick)
                self._high = tick_diff

    def pulse_period(self):
        """
        Returns the PWM period
        """
        if self._period is not None:
            return self._period
        else:
            return 0.0

    def pulse_width(self):
        """
        Returns the PWM pulse width in microseconds.
        """
        if self._high is not None:
            return self._high
        else:
            return 0.0

    def cancel(self):
        """
        Cancels the reader and releases resources.
        """
        self._cb.cancel()
