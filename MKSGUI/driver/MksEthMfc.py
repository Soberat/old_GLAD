import logging
from dataclasses import dataclass
from enum import Enum
from queue import Queue
from typing import Callable, Any

from PyQt5.QtCore import QRunnable, QObject, pyqtSignal
from pyModbusTCP.utils import decode_ieee, word_list_to_long

from driver.FloatModbusClient import FloatModbusClient


class MksEthMfcValveState(Enum):
    NORMAL = 0
    CLOSED = 1
    OPEN = 2


class MksEthMfc:

    def __init__(self, host_ip_address: str):
        self.modbus_client = FloatModbusClient(host=host_ip_address, port=502, unit_id=1, auto_open=True)

    def get_flow(self) -> float:
        return decode_ieee(word_list_to_long(self.modbus_client.read_input_registers(0x4000, 2))[0])

    def get_temperature(self) -> float:
        return decode_ieee(word_list_to_long(self.modbus_client.read_input_registers(0x4002, 2))[0])

    def get_valve_position(self) -> float:
        return decode_ieee(word_list_to_long(self.modbus_client.read_input_registers(0x4004, 2))[0])

    def get_flow_hours(self) -> int:
        return word_list_to_long(self.modbus_client.read_input_registers(0x4008, 2))[0]

    def get_flow_total(self) -> float:
        return word_list_to_long(self.modbus_client.read_input_registers(0x400A, 2))[0]

    def get_setpoint(self) -> float:
        return self.modbus_client.read_float(0xA000, 2)[0]

    def set_setpoint(self, setpoint: float) -> bool:
        return self.modbus_client.write_float(0xA000, [setpoint])

    def get_ramp_rate(self) -> int:
        return self.modbus_client.read_holding_registers(0xA002, 2)[0]

    def set_ramp_rate(self, ramp_rate: int) -> bool:
        return self.modbus_client.write_float(0xA002, [ramp_rate])

    def get_unit_type(self) -> int:
        return self.modbus_client.read_holding_registers(0xA004, 2)[0]

    def set_unit_type(self, unit_type: int) -> bool:
        return self.modbus_client.write_multiple_registers(0xA004, [unit_type])

    def reset(self) -> bool:
        return self.modbus_client.write_single_coil(0xE000, True)

    def set_valve_state(self, state: MksEthMfcValveState) -> bool:
        return self.modbus_client.write_single_coil(0xE001, state == MksEthMfcValveState.OPEN)\
               and self.modbus_client.write_single_coil(0xE002, state == MksEthMfcValveState.CLOSED)

    def get_valve_state(self) -> MksEthMfcValveState:
        is_open = self.modbus_client.read_coils(0xE001)
        is_closed = self.modbus_client.read_coils(0xE002)

        if is_open:
            return MksEthMfcValveState.OPEN
        elif is_closed:
            return MksEthMfcValveState.CLOSED
        else:
            return MksEthMfcValveState.NORMAL

    def set_flow_zero(self, is_zero: bool) -> bool:
        return self.modbus_client.write_single_coil(0xE003, is_zero)


class MksEthMfcWorkerSignals(QObject):
    flow_ready = pyqtSignal(float)
    empty = pyqtSignal(bool)


@dataclass(order=True)
class MksEthMfcWorkerTask:
    signal: pyqtSignal
    func: Callable[[Any], Any]
    error_return: Any


class MksEthMfcWorker(QRunnable, QObject):
    def __init__(self):
        super().__init__()
        self.signals = MksEthMfcWorkerSignals()
        self.task_queue = Queue()

    def run(self):
        while True:
            logging.debug("Waiting for task")
            task = self.task_queue.get(block=True)
            logging.debug("New task with func {}".format(task.func.__qualname__))
            try:
                task.signal.emit(task.func())
            except Exception:
                logging.warning("Task failed")
                task.signal.emit(task.error_return)
