import ipaddress
from enum import Enum
from typing import Iterable

import pymodbus.exceptions
from pymodbus.client import ModbusSerialClient
from PyQt5.QtCore import QObject, pyqtSignal


class InputState(Enum):
    LOW = 0
    HIGH = 1
    UNKNOWN = 2


class WP8026ADAM(QObject):

    stateChanged = pyqtSignal(int, InputState)

    def __init__(self, comport: str):
        super().__init__()

        self.__modbus_client = ModbusSerialClient(comport, baudrate=9600, parity="N", stopbits=1, bytesize=8)

        if not self.__modbus_client.connect():
            raise pymodbus.exceptions.ModbusException(f"Failed to connect to WP8026ADAM on port {comport}")

    def get_input_states(self, input_n: int = -1) -> Iterable[InputState]:
        assert -1 <= input_n <= 15

        if self.__modbus_client.send([0x01, 0x02, 0x00, 0x00, 0x00, 0x10, 0x79, 0xc6]):
            response = self.__modbus_client.recv(8)
            if not response:
                return [InputState.UNKNOWN]*16 if input_n == -1 else [InputState.UNKNOWN]

            response = format(int.from_bytes(response[3:5], byteorder="little"), "#018b")[2:]

            return [InputState(int(state)) for state in response][::-1] if input_n == -1 \
                else [InputState(response[input_n])]

        return [InputState.UNKNOWN] * 16 if input_n == -1 else [InputState.UNKNOWN]


if __name__ == '__main__':
    x = WP8026ADAM("COM4")
    [print(y) for y in list(enumerate(x.get_input_states()))]