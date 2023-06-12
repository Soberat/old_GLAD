import inspect

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton, QLineEdit, QLabel, QHBoxLayout, QGroupBox, \
    QTextEdit
from serial.tools.list_ports import comports

from driver.RX01 import RX01
from gui.ButtonWithEdits import ButtonWithEdits


class RX01Widget(QWidget):
    def __init__(self):
        super().__init__()

        self.device = None

        self.setLayout(QVBoxLayout())

        self.comport_dropdown = QComboBox()
        self.comport_dropdown.addItems([comport.name for comport in comports()])

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_device)

        self.device_group = QGroupBox()
        self.device_group.setEnabled(False)
        self.device_group.setLayout(QVBoxLayout())

        # Populate the device group
        # Simple functions with no arguments and simple return value
        for func_name in ["assert_serial_control",
                          "assert_analog_control",
                          "assert_panel_control",
                          "enable_serial_echo_mode",
                          "disable_serial_echo_mode",
                          "set_exciter_mode_to_master",
                          "set_exciter_mode_to_slave",
                          "select_forward_power_leveling",
                          "select_load_power_leveling",
                          "select_power_control_mode",
                          "select_voltage_control_mode",
                          "disable_power_and_rf_output",
                          "enable_pulse_mode",
                          "disable_pulse_mode",
                          "enable_variable_frequency_tuning",
                          "disable_variable_frequency_tuning",
                          "enable_rf_output",
                          "disable_rf_output",
                          "enable_rf_output_ramping",
                          "disable_rf_output_ramping",
                          "get_forward_power_output",
                          "get_reflected_power",
                          "get_dc_bias_voltage",
                          "get_control_voltage",
                          "get_power_leveling_mode",
                          "get_maximum_power",
                          "get_mc2_load_cap_preset_position",
                          "get_mc2_tune_cap_preset_position",
                          "get_mc2_phase_voltage",
                          "get_mc2_magnitude_voltage"]:

            visible_action_name = func_name.replace("_", " ")

            bwe = ButtonWithEdits(visible_action_name, self.device, func_name, [], {})

            self.device_group.layout().addWidget(bwe)

        # Functions with parameters and simple responses
        for func_name in ["set_mc2_tune_cap_preset_position",
                          "set_mc2_load_cap_preset_position",
                          "set_operating_frequency",
                          "set_power_setpoint",
                          "set_power_setpoint_and_enable_rf_output",
                          "set_voltage_setpoint",
                          "set_process_pulse_duty_cycle",
                          "set_process_pulse_frequency",
                          "set_process_pulse_high_time",
                          "set_process_pulse_low_power_setpoint",
                          "set_vft_coarse_trip_ratio",
                          "set_vft_coarse_frequency_step",
                          "set_vft_fine_frequency_step",
                          "set_vft_fine_trip_level",
                          "set_maximum_vft_frequency",
                          "set_minimum_vft_frequency",
                          "set_vft_strike_frequency",
                          "set_rf_output_rampdown_time_interval",
                          "set_rf_output_rampup_time_interval"]:

            argspec = inspect.getfullargspec(getattr(RX01, func_name))
            args = argspec.args[1:]
            annotations = argspec.annotations

            visible_action_name = func_name.replace("_", " ")
            bwe = ButtonWithEdits(visible_action_name, self.device, func_name, args, annotations)

            self.device_group.layout().addWidget(bwe)

        for func_name in ["get_short_status", "get_long_status"]:
            visible_action_name = func_name.replace("_", " ")

            bwe = ButtonWithEdits(visible_action_name, self.device, func_name, [], {}, output_class=QTextEdit)
            bwe.output.setMinimumWidth(500)
            bwe.output.setReadOnly(True)

            self.device_group.layout().addWidget(bwe)

        temp_layout = QHBoxLayout()

        temp_layout.addWidget(self.comport_dropdown)
        temp_layout.addWidget(self.connect_button)

        self.layout().addLayout(temp_layout)

        self.layout().addWidget(self.device_group)

    def connect_device(self):
        self.device = RX01(RX01.RX01Model.R301, comport=self.comport_dropdown.currentText())
        self.connect_button.setText("Disconnect")
        self.connect_button.clicked.disconnect(self.connect_device)
        self.connect_button.clicked.connect(self.disconnect_device)
        self.device_group.setEnabled(True)
        # Update the target for all ButtonWithEdits
        for widget in self.device_group.children():
            if isinstance(widget, ButtonWithEdits):
                widget.target = self.device

    def disconnect_device(self):
        self.device = None
        self.connect_button.setText("Connect")
        self.connect_button.clicked.disconnect(self.disconnect_device)
        self.connect_button.clicked.connect(self.connect_device)
        self.device_group.setEnabled(False)
        # Update the target for all ButtonWithEdits
        for widget in self.device_group.children():
            if isinstance(widget, ButtonWithEdits):
                widget.target = None
