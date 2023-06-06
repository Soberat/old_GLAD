import enum
from enum import Enum
import ipaddress
from typing import Iterable

from PyQt5.QtCore import QObject, pyqtSignal
from pyModbusTCP.client import ModbusClient


class RelayState(Enum):
    # TODO: determine if open/closed is 0/1 or 1/0
    OPEN = 0
    CLOSED = 1
    UNKNOWN = enum.auto()


class SR201(QObject):

    stateChanged = pyqtSignal(int, RelayState)

    def __init__(self, ipv4_address: ipaddress.IPv4Address, mode: str = "tcp"):
        super().__init__()
        if mode.lower() != "tcp":
            raise ValueError("Non-TCP modes are not currently supported")

        self.__modbus_client = ModbusClient(host=ipv4_address.exploded, port=6724)

        self.__modbus_client.debug = True

    def get_relay_states(self, relay_n: int = -1) -> Iterable[RelayState]:
        response = self.__modbus_client.read_coils(0, 16)

        if not response:
            for i in range(0, 16):
                self.stateChanged.emit(i, RelayState.UNKNOWN)
            return [RelayState.UNKNOWN]*16 if relay_n == -1 else [RelayState.UNKNOWN]

        for idx, state in enumerate(response):
            self.stateChanged.emit(idx, RelayState(state))
        return [RelayState(state) for state in response] if relay_n == -1 else [RelayState(response[relay_n])]

    def set_relay_state(self, relay_n: int, state: RelayState, duration: int = -1) -> bool:
        assert 0 <= relay_n <= 15

        if duration == -1:
            # Write a coil to set state without timeout
            if self.__modbus_client.write_single_coil(relay_n, state.value):
                self.stateChanged.emit(relay_n, state)
                return True
            else:
                self.stateChanged.emit(relay_n, RelayState.UNKNOWN)
                return False

        if self.__modbus_client.write_single_register(relay_n, duration):
            self.stateChanged.emit(relay_n, state)
            return True
        else:
            self.stateChanged.emit(relay_n, RelayState.UNKNOWN)
            return False
