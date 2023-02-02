import io
from enum import Enum

import serial
import logging

from serial import SerialException


class StepperController:
    class StepperOperatingMode(Enum):
        SERVO_MODE = 1
        OPEN_LOOP_STEPPER_MODE = 11
        CHECKING_STEPPER_MODE = 12
        EXTERNAL_LOOP_STEPPER_MODE = 13
        CLOSED_LOOP_STEPPER_MODE = 14

    def __init__(self, comport='COM3', baudrate=9600, parity=serial.PARITY_EVEN, databits=serial.SEVENBITS,
                 stopbits=serial.STOPBITS_ONE, xonxoff=False):
        try:
            logging.debug("Setting up serial with params: {}".format(locals()))
            self.__serial = serial.Serial(baudrate=baudrate,
                                          parity=parity,
                                          bytesize=databits,
                                          stopbits=stopbits,
                                          timeout=100,
                                          port=comport)
        except ValueError as ve:
            logging.exception("One of args passed to Serial was out of bounds (Err:{}): {}".format(ve, locals()))
        except SerialException as se:
            logging.exception("Device not found or cannot be configured (Err:{})".format(se))

        logging.debug("Opening serial")
        if not self.__serial.isOpen():
            self.__serial.open()
        logging.debug("Serial open")

    def write(self, axis, command, value=None):
        if value:
            self.__serial.write("{}{}{}\r".format(axis, command, value).encode())
            logging.debug("Write command '{}{}{}'".format(axis, command, value))
        else:
            self.__serial.write("{}{}\r".format(axis, command).encode())
            logging.debug("Write command '{}{}'".format(axis, command))
        readback = self.__serial.read_until().decode()
        logging.debug("Readback: {}".format(readback))
        return "OK" in readback.upper()

    def read(self, axis, command):
        logging.debug("Read command: {}{}".format(axis, command))
        self.__serial.write("{}{}\r".format(axis, command).encode("utf-8"))
        readback = self.__serial.read_until()
        logging.debug("Readback: {}".format(readback))
        return readback


class StepperControllerAxis:
    def __init__(self, stepper_controller: StepperController, axis_number: int):
        #assert 1 <= axis_number <= 99
        self.stepper_controller = stepper_controller
        self.axis_number = axis_number

    """
    Getting started commands
    """

    def help_pages(self):
        return self.stepper_controller.read(self.axis_number, "HE")

    def display_next_page(self):
        return self.stepper_controller.read(self.axis_number, "HN")

    def display_previous_page(self):
        return self.stepper_controller.read(self.axis_number, "HP")

    def initialize(self):
        return self.stepper_controller.read(self.axis_number, "IN")

    def query_speeds(self):
        return self.stepper_controller.read(self.axis_number, "QS")

    def query_all(self):
        return self.stepper_controller.read(self.axis_number, "QA")

    """
    Abort, Stop & Reset commands
    """

    def hard_stop(self):
        return self.stepper_controller.read(self.axis_number, "\u0003")

    def soft_stop(self):
        return self.stepper_controller.read(self.axis_number, "ST")

    def set_abort_mode(self, a: bool, b: bool, c: bool, d: bool, e: bool, f: bool, g: bool, h: bool):
        """
        :param a: 0 – Abort Stop Input disables control loop
                  1 – Abort Stop Input stops all moves only
        :param b: 0 – Abort Stop Input is latched requiring RS command to reset
                  1 – Abort Stop Input is only momentary
        :param c: 0 – Stall Error disables control loop
                  1 – Stall Error is indicated but control loop remains active
        :param d: 0 – Tracking Error disables control loop
                  1 – Tracking Error is indicated but control loop remains active
        :param e: 0 – TimeOut Error disables control loop
                  1 – TimeOut Error is indicated but control loop remains active
        :param f: Reserved for future use
        :param g: Reserved for future use
        :param h: 0 – Enable output switched OFF during a disabled control loop
                  1 – Enable output left ON during a control loop abort
        """
        return self.stepper_controller.write(self.axis_number, "AM",
                                             "{}{}{}{}{}{}{}{}".format(int(a), int(b), int(c), int(d), int(e),
                                                                       int(f), int(g), int(h)))

    def command_abort(self):
        return self.stepper_controller.read(self.axis_number, "AB")

    def reset(self):
        return self.stepper_controller.read(self.axis_number, "RS")

    def query_modes(self):
        return self.stepper_controller.read(self.axis_number, "QM")

    """
    Information
    """

    def display_current_operation(self):
        return self.stepper_controller.read(self.axis_number, "CO")

    def identify_version(self):
        return self.stepper_controller.read(self.axis_number, "ID")

    def output_command_position(self):
        return self.stepper_controller.read(self.axis_number, "OC")

    def output_actual_position(self):
        return self.stepper_controller.read(self.axis_number, "OA")

    def output_datum_position(self):
        return self.stepper_controller.read(self.axis_number, "OD")

    def output_velocity(self):
        return self.stepper_controller.read(self.axis_number, "OV")

    def output_status_string(self):
        return self.stepper_controller.read(self.axis_number, "OS")

    def output_following_error(self):
        return self.stepper_controller.read(self.axis_number, "OF")

    def query_positions(self):
        return self.stepper_controller.read(self.axis_number, "QP")

    def query_privilege_level(self):
        return self.stepper_controller.read(self.axis_number, "QL")

    """
    Set Up
    """

    def set_command_mode(self, mode: StepperController.StepperOperatingMode):
        return self.stepper_controller.write(self.axis_number, "CM", mode.value)

    def set_encoder_ratio(self, numerator: int, denominator: int):
        return self.stepper_controller.write(self.axis_number, "ER", "{}/{}".format(numerator, denominator))

    def set_backoff_steps(self, steps: int):
        ##assert -32000 <= steps <= 32000
        return self.stepper_controller.write(self.axis_number, "BO", steps)

    def set_creep_steps(self, steps):
        ##assert 0 <= steps <= 2147483647
        return self.stepper_controller.write(self.axis_number, "CR", steps)

    def set_timeout(self, milliseconds):
        ##assert 1 <= milliseconds <= 60000
        return self.stepper_controller.write(self.axis_number, "TO", milliseconds)

    def set_settling_time(self, milliseconds):
        ##assert 0 <= milliseconds <= 20000
        return self.stepper_controller.write(self.axis_number, "SE", milliseconds)

    def set_settling_window(self, steps):
        ##assert 0 <= steps <= 2147483647
        return self.stepper_controller.write(self.axis_number, "WI", steps)

    """
    Fault detection features
    """

    def set_soft_limits(self, enabled: bool):
        return self.stepper_controller.write(self.axis_number, "SL", int(enabled))

    def set_tracking_window(self, steps):
        ##assert 0 <= steps <= 2147483647
        return self.stepper_controller.write(self.axis_number, "TR", steps)

    """
    Datuming
    """

    def clear_captured_datum_position(self):
        return self.stepper_controller.read(self.axis_number, "CD")

    def go_home_to_datum(self, positive_direction: bool):
        return self.stepper_controller.write(self.axis_number, "HD", "" if positive_direction else "-1")

    def move_to_datum_position(self):
        return self.stepper_controller.read(self.axis_number, "MD")

    def set_home_position(self, home_position):
        ##assert -2147483647 <= home_position <= 2147483647
        return self.stepper_controller.write(self.axis_number, "SH", home_position)

    def set_datum_mode(self, a: int, b: int, c: int, d: int, e: int, f: int, g: int, h: int):
        """
        :param a: 0 – Encoder index input polarity is normal
                  1 – Encoder index input polarity is inverted
        :param b: 0 – Datum point is captured only once (i.e. after HD command)
                  1 – Datum point is captured each time it happens
        :param c: 0 – Datum position is captured but not changed
                  1 – Datum position is set to Home Position (SH) after datum search (HD)
        :param d: 0 – Automatic direction search disabled
                  1 – Automatic direction search enabled
        :param e: 0 – Automatic opposite limit search disabled
                  1 – Automatic opposite limit search enabled
        :param f: Reserved for future use
        :param g: Reserved for future use
        :param h: Reserved for future use
        """
        return self.stepper_controller.write(self.axis_number, "DM",
                                             "{}{}{}{}{}{}{}{}".format(int(a), int(a), int(b), int(c),
                                                                       int(d), int(e), int(f), int(g), int(h)))

    """
    Position commands
    """

    def set_actual_position(self, position):
        ##assert -2147483647 <= position <= 2147483647
        return self.stepper_controller.write(self.axis_number, "AP", position)

    def set_command_position(self, value):
        ##assert -2147483647 <= value <= 2147483647
        return self.stepper_controller.write(self.axis_number, "CP", value)

    def difference_actual_position(self, position):
        ##assert -2147483647 <= position <= 2147483647
        return self.stepper_controller.write(self.axis_number, "DA", position)

    """
    Speed, acceleration and deceleration
    """

    def constant_velocity_move(self, steps_per_second):
        ##assert -1200000 <= steps_per_second <= 1200000
        return self.stepper_controller.write(self.axis_number, "CV", steps_per_second)

    def set_creep_speed(self, steps_per_second):
        ##assert 1 <= steps_per_second <= 400000
        return self.stepper_controller.write(self.axis_number, "SC", steps_per_second)

    def set_fast_jog_speed(self, steps_per_second):
        ##assert 1 <= steps_per_second <= 200000
        return self.stepper_controller.write(self.axis_number, "SF", steps_per_second)

    def set_slow_jog_speed(self, steps_per_second):
        #assert 1 <= steps_per_second <= 20000
        return self.stepper_controller.write(self.axis_number, "SJ", steps_per_second)

    def set_velocity(self, steps_per_second):
        #assert 1 <= steps_per_second <= 1200000
        return self.stepper_controller.write(self.axis_number, "SV", steps_per_second)

    def set_acceleration(self, acceleration):
        #assert 1 <= acceleration <= 20000000
        return self.stepper_controller.write(self.axis_number, "SA", acceleration)

    def set_deceleration(self, deceleration):
        #assert 1 <= deceleration <= 20000000
        return self.stepper_controller.write(self.axis_number, "SD", deceleration)

    def set_limit_deceleration(self, deceleration):
        #assert 1 <= deceleration <= 20000000
        return self.stepper_controller.write(self.axis_number, "LD", deceleration)

    """
    Moves
    """

    def move_absolute(self, steps):
        #assert -2147483647 <= steps <= 2147483647
        return self.stepper_controller.write(self.axis_number, "MA", steps)

    def move_relative(self, steps):
        #assert -2147483647 <= steps <= 2147483647
        return self.stepper_controller.write(self.axis_number, "MR", steps)

    def set_delay_time(self, milliseconds):
        #assert 1 <= milliseconds <= 2000000
        return self.stepper_controller.write(self.axis_number, "DE", milliseconds)

    """
    Soft limits
    """

    def set_lower_soft_limit(self, position):
        #assert -2147483647 <= position <= 2147483647
        return self.stepper_controller.write(self.axis_number, "LL", position)

    def set_upper_soft_limit(self, position):
        #assert -2147483647 <= position <= 2147483647
        return self.stepper_controller.write(self.axis_number, "UL", position)

    """
    End of move
    """

    def wait_for_end_of_current_move(self):
        return self.stepper_controller.read(self.axis_number, "WE")

    """
    Read & write ports
    """

    def read_port(self):
        return self.stepper_controller.read(self.axis_number, "RP")

    def write_port(self, bit_pattern: str):
        return self.stepper_controller.write(self.axis_number, "WP", bit_pattern)

    def wait_for_input_event(self, bit_pattern: str):
        return self.stepper_controller.write(self.axis_number, "WA", bit_pattern)

    def do_next_command_if_false(self, bit_pattern: str):
        return self.stepper_controller.write(self.axis_number, "IF", bit_pattern)

    def do_next_command_if_true(self, bit_pattern: str):
        return self.stepper_controller.write(self.axis_number, "IT", bit_pattern)

    """
    Jog
    """

    def set_jog_mode(self, a: int, b: int, c: int, d: int, e: int, f: int, g: int, h: int):
        """
        :param a: 0 – Jog switch inputs disabled
                  1 – Jog switch inputs enabled
        :param b: 0 – Joystick input disabled
                  1 – Joystick input enabled
        :param c: 0 – Input encoder jog input disabled
                  1 – Input encoder jog input enabled
        :param d: 0 – Jog Select (channel increment) disabled
                  1 - Jog Select (channel increment) enabled
        :param e: Reserved for future use
        :param f: Reserved for future use
        :param g: Reserved for future use
        :param h: Reserved for future use
        """
        return self.stepper_controller.write(self.axis_number, "JM",
                                             "{}{}{}{}{}{}{}{}".format(int(a), int(a), int(b), int(c),
                                                                       int(d), int(e), int(f), int(g), int(h)))

    def set_joystick_centre_position(self, position):
        #assert 0 <= position <= 4095
        return self.stepper_controller.write(self.axis_number, "JC", position)

    def set_joystick_range(self, position):
        #assert 100 <= position <= 4095
        return self.stepper_controller.write(self.axis_number, "JS", position)

    def set_joystick_speed(self, steps_per_second):
        #assert 1 <= steps_per_second <= 400000
        return self.stepper_controller.write(self.axis_number, "JS", steps_per_second)

    def set_joystick_threshold(self, value):
        #assert 1 <= value <= 4095
        return self.stepper_controller.write(self.axis_number, "JT", value)

    def query_joystick_settings(self):
        return self.stepper_controller.read(self.axis_number, "QJ")

    """
    Sequences
    """

    def auto_execute_sequence(self, sequence_no: int):
        return self.stepper_controller.write(self.axis_number, "AE", sequence_no)

    def auto_execute_disable(self):
        return self.stepper_controller.read(self.axis_number, "AD")

    def define_sequence(self, sequence_no: int):
        return self.stepper_controller.write(self.axis_number, "DS", sequence_no)

    def end_sequence_definition(self):
        return self.stepper_controller.read(self.axis_number, "ES")

    def list_sequence(self, sequence_no: int):
        return self.stepper_controller.write(self.axis_number, "LS", sequence_no)

    def execute_sequence(self, sequence_no: int):
        return self.stepper_controller.write(self.axis_number, "XS", sequence_no)

    def backup_sequence(self):
        return self.stepper_controller.read(self.axis_number, "BS")

    def undefine_sequence(self, sequence_no: int):
        return self.stepper_controller.write(self.axis_number, "US", sequence_no)

    """
    Help
    """

    def help_with_modes_commands(self):
        return self.stepper_controller.read(self.axis_number, "HM")

    def help_with_status_output_message(self):
        return self.stepper_controller.read(self.axis_number, "HS")

    def help_with_command_modes(self):
        return self.stepper_controller.read(self.axis_number, "HC")

    """
    Privilege level
    """

    def new_pin(self, new_pin: str):
        #assert len(new_pin) == 4 and 0 <= int(new_pin) <= 9999
        return self.stepper_controller.write(self.axis_number, "NP", new_pin)

    def enter_pin(self, pin: str):
        #assert len(pin) == 4 and 0 <= int(pin) <= 9999
        return self.stepper_controller.write(self.axis_number, "PI", pin)

    def set_privilege_level(self, privilege_level: int):
        #assert 0 <= privilege_level <= 9
        return self.stepper_controller.write(self.axis_number, "PL", privilege_level)

    """
    Backup
    """

    def backup_all(self):
        return self.stepper_controller.read(self.axis_number, "BA")

    def backup_sequences(self):
        return self.stepper_controller.read(self.axis_number, "BS")

    def backup_digiloop_parameters(self):
        return self.stepper_controller.read(self.axis_number, "BD")
