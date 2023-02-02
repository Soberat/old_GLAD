import logging
from dataclasses import dataclass

import serial


@dataclass
class VGC403PressureSensorData:
    status: int
    value: float
    error: float


class VGC403:

    PR_STATUS_STRINGS = {
        0: "OK",
        1: "underrange",
        2: "overrange",
        3: "sensor error",
        4: "sensor switched off",
        5: "no sensor",
        6: "identification error",
        7: "BPG/HPG error"
    }

    def __init__(self, comport='COM1', baudrate=9600, parity=serial.PARITY_NONE, databits=serial.EIGHTBITS,
                 stopbits=serial.STOPBITS_ONE):
        self.__serial = serial.Serial(baudrate=baudrate,
                                      parity=parity,
                                      bytesize=databits,
                                      stopbits=stopbits,
                                      timeout=100,
                                      port=comport)

    def read_pressure_sensor(self, sensor_number: int):
        assert sensor_number in [1, 2, 3]
        logging.info(f"Sending 'PR{sensor_number}'\r")
        self.__serial.write(f"PR{sensor_number}\r".encode())
        logging.info(f"Readback: {self.__serial.readline()}")
        logging.info(f"Sending '{chr(0x05)}'")
        self.__serial.write(f"{chr(0x05)}".encode())
        logging.info("Reading back info")
        readback_string = self.__serial.readline().decode()
        logging.info(readback_string)
        logging.info(f"Extracted info: {int(readback_string[0]), float(readback_string[2:9]), int(readback_string[10:13])}")
        return VGC403PressureSensorData(int(readback_string[0]), float(readback_string[2:9]), int(readback_string[10:13]))

    def get_pr_status_string(self, status: int) -> str:
        return self.PR_STATUS_STRINGS[status]
