from dataclasses import dataclass

import serial
import minimalmodbus

def parse_int_to_float(func):
    """
    Parse a float returned by the device according to the documentation, as in divide by 10

    :return: function that returns value parsed to float
    """
    def wrapper(*args, **kwargs):
        return float(func(*args, **kwargs))/10
    return wrapper

class TempController32h8i(minimalmodbus.Instrument):
    @dataclass
    class InstrumentStatus:
        alarm1_status: bool
        alarm2_status: bool
        alarm3_status: bool
        alarm4_status: bool
        sensor_break_status: bool
        pv_overrange_status: bool
        new_alarm_status: bool

    BAUD_RATES = [1200, 2400, 4800, 9600, 19200]

    def __init__(self, slave_address, comport='COM1', baudrate=9600, parity=serial.PARITY_NONE,
                 databits=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE):
        minimalmodbus.Instrument.__init__(self, comport, slave_address)

        if baudrate in self.BAUD_RATES:
            self.serial.baudrate = baudrate
        else:
            raise ValueError("Baud rate of {} not allowed".format(baudrate))

        self.serial.parity = parity
        self.serial.bytesize = databits
        self.serial.stopbits = stopbits

    def set_process_value(self, process_value: float, is_comms_value: bool) -> bool:
        if is_comms_value:
            self.write_register(203, int(process_value*10))
        else:
            self.write_register(1, int(process_value * 10))
        return True

    @parse_int_to_float
    def get_process_value(self, is_comms_value: bool) -> float:
        if is_comms_value:
            return self.read_register(203)*10
        else:
            return self.read_register(1)*10

    def set_setpoint_value(self, setpoint_value: float) -> bool:
        self.write_register(26, int(setpoint_value*10))
        return True

    @parse_int_to_float
    def get_setpoint_value(self) -> float:
        return self.read_register(26)

    @parse_int_to_float
    def get_input_range_low(self) -> float:
        return self.read_register(11)

    def set_input_range_low(self, range_limit: float) -> bool:
        self.write_register(11, int(range_limit*10))
        return True

    @parse_int_to_float
    def get_input_range_high(self) -> float:
        return self.read_register(12)

    def set_input_range_high(self, range_limit: float) -> bool:
        self.write_register(12, int(range_limit*10))
        return True

    def get_instrument_status(self) -> InstrumentStatus:
        bit_values = bin(self.read_register(75))  # do [::-1] if the order is wrong
        status = self.InstrumentStatus(
            alarm1_status=bool(bit_values[0]),
            alarm2_status=bool(bit_values[1]),
            alarm3_status=bool(bit_values[2]),
            alarm4_status=bool(bit_values[3]),
            sensor_break_status=bool(bit_values[5]),
            pv_overrange_status=bool(bit_values[10]),
            new_alarm_status=bool(bit_values[12]))

        return status

    @parse_int_to_float
    def get_pv_offset(self) -> float:
        return self.read_register(141)

    def set_pv_offset(self, pv_offset: float):
        self.write_register(141, int(pv_offset*10))
        return True
