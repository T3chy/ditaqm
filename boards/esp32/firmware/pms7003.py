# original source: https://github.com/pkucmus/micropython-pms7003/blob/master/pms7003.py
# modified by Elam Day-Friedland Mar 9, 2021
"""
A class for interacting with the PMS7003 particulate matter sensor
"""
import machine
import struct
import time



class UartError(Exception):
    pass


class Pms7003:

    START_BYTE_1 = 0x42
    START_BYTE_2 = 0x4d

    PMS_FRAME_LENGTH = 0
    PMS_PM1_0 = 1
    PMS_PM2_5 = 2
    PMS_PM10_0 = 3
    PMS_PM1_0_ATM = 4
    PMS_PM2_5_ATM = 5
    PMS_PM10_0_ATM = 6
    PMS_PCNT_0_3 = 7
    PMS_PCNT_0_5 = 8
    PMS_PCNT_1_0 = 9
    PMS_PCNT_2_5 = 10
    PMS_PCNT_5_0 = 11
    PMS_PCNT_10_0 = 12
    PMS_VERSION = 13
    PMS_ERROR = 14
    PMS_CHECKSUM = 15

    def __init__(self, uart=None):
        if uart:
            self.uart = machine.UART(uart, baudrate=9600, bits=8, parity=None, stop=1)
        else:
            self.uart = uart = machine.UART(2, baudrate=9600, bits=8, parity=None, stop=1, tx=17, rx=16, rts=-1, cts=-1, txbuf=256, rxbuf=256, timeout=500)
    def __repr__(self):
        return "Pms7003({})".format(self.uart)

    @staticmethod
    def _assert_byte(byte, expected):
        if byte is None or len(byte) < 1 or ord(byte) != expected:
            return False
        return True

    @staticmethod
    def _format_bytearray(buffer):
        return "".join("0x{:02x} ".format(i) for i in buffer)

    def _send_cmd(self, request, response):

        nr_of_written_bytes = self.uart.write(request)

        if nr_of_written_bytes != len(request):
            raise UartError("Failed to write to UART")

        if response:
            time.sleep(2)
            buffer = self.uart.read(len(response))

            if buffer != response:
                raise UartError(
                    "Wrong UART response, expecting: {}, getting: {}".format(
                        Pms7003._format_bytearray(response), Pms7003._format_bytearray(buffer)
                    )
                )

    def read(self):

        while True:

            first_byte = self.uart.read(1)
            if not self._assert_byte(first_byte, Pms7003.START_BYTE_1):
                continue

            second_byte = self.uart.read(1)
            if not self._assert_byte(second_byte, Pms7003.START_BYTE_2):
                continue

            # we are reading 30 bytes left
            read_bytes = self.uart.read(30)
            if len(read_bytes) < 30:
                continue

            data = struct.unpack("!HHHHHHHHHHHHHBBH", read_bytes)

            checksum = Pms7003.START_BYTE_1 + Pms7003.START_BYTE_2
            checksum += sum(read_bytes[:28])

            if checksum != data[Pms7003.PMS_CHECKSUM]:
                continue

            return {
                "FRAME_LENGTH": data[Pms7003.PMS_FRAME_LENGTH],
                "pm1_0": data[Pms7003.PMS_PM1_0],
                "pm2_5": data[Pms7003.PMS_PM2_5],
                "pm10_0": data[Pms7003.PMS_PM10_0],
                "pm1_0_atm": data[Pms7003.PMS_PM1_0_ATM],
                "pm2_5_atm": data[Pms7003.PMS_PM2_5_ATM],
                "pm10_0_atm": data[Pms7003.PMS_PM10_0_ATM],
                "pcnt_0_3": data[Pms7003.PMS_PCNT_0_3],
                "pcnt_0_5": data[Pms7003.PMS_PCNT_0_5],
                "pcnt_1_0": data[Pms7003.PMS_PCNT_1_0],
                "pcnt_2_5": data[Pms7003.PMS_PCNT_2_5],
                "pcnt_5_0": data[Pms7003.PMS_PCNT_5_0],
                "pcnt_10_0": data[Pms7003.PMS_PCNT_10_0],
                "versiON": data[Pms7003.PMS_VERSION],
                "error": data[Pms7003.PMS_ERROR],
                "checksum": data[Pms7003.PMS_CHECKSUM],
            }


class PassivePms7003(Pms7003):
    """
    More about passive mode here:
    https://github.com/teusH/MySense/blob/master/docs/pms7003.md
    https://patchwork.ozlabs.org/cover/1039261/
    https://joshefin.xyz/air-quality-with-raspberrypi-pms7003-and-java/
    """
    ENTER_PASSIVE_MODE_REQUEST = bytearray(
        [Pms7003.START_BYTE_1, Pms7003.START_BYTE_2, 0xe1, 0x00, 0x00, 0x01, 0x70]
    )
    ENTER_PASSIVE_MODE_RESPONSE = bytearray(
        [Pms7003.START_BYTE_1, Pms7003.START_BYTE_2, 0x00, 0x04, 0xe1, 0x00, 0x01, 0x74]
    )
    SLEEP_REQUEST = bytearray(
        [Pms7003.START_BYTE_1, Pms7003.START_BYTE_2, 0xe4, 0x00, 0x00, 0x01, 0x73]
    )
    SLEEP_RESPONSE = bytearray(
        [Pms7003.START_BYTE_1, Pms7003.START_BYTE_2, 0x00, 0x04, 0xe4, 0x00, 0x01, 0x77]
    )
    # NO response
    WAKEUP_REQUEST = bytearray(
        [Pms7003.START_BYTE_1, Pms7003.START_BYTE_2, 0xe4, 0x00, 0x01, 0x01, 0x74]
    )
    # data as response
    READ_IN_PASSIVE_REQUEST = bytearray(
        [Pms7003.START_BYTE_1, Pms7003.START_BYTE_2, 0xe2, 0x00, 0x00, 0x01, 0x71]
    )

    def __init__(self, uart=None):
        super().__init__(uart=uart)
        # use passive mode pms7003
        self._send_cmd(request=PassivePms7003.ENTER_PASSIVE_MODE_REQUEST,
                       response=PassivePms7003.ENTER_PASSIVE_MODE_RESPONSE)

    def sleep(self):
        self._send_cmd(request=PassivePms7003.SLEEP_REQUEST,
                       response=PassivePms7003.SLEEP_RESPONSE)

    def wakeup(self):
        self._send_cmd(request=PassivePms7003.WAKEUP_REQUEST, response=None)

    def read(self):
        self._send_cmd(request=PassivePms7003.READ_IN_PASSIVE_REQUEST, response=None)
        return super().read()
