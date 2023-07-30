import inspect

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton, QLineEdit, QLabel, QHBoxLayout, QGroupBox, \
    QTextEdit
from serial.tools.list_ports import comports

from driver.PD500X1 import PD500X1
from gui.ButtonWIthEdits import ButtonWithEdits


class PD500X1Widget(QWidget):
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
        for func_name in [
            "set_analog_control",
            "set_rs232_control",
            "enable_output",
            "disable_output",
            "clear_active_target_kwh_count"
            "reset_factory_defaults",
            "enable_repeat_mode",
            "disable_repeat_mode",
            "enable_echo_mode",
            "disable_echo_mode",
            "read_hard_arc_count",
            "read_micro_arc_count",
            "read_active_target_Number",
            "read_actual_power_in_Watts",
            "read_actual_current_in_amps",
            "read_actual_voltage_in_volts",
            "read_arc_rate_in_arcs_per_second",
            "read_heartbeat_timeout_in_seconds",
            "read_active_target_power_setpoint_in_Watts",
            "read_active_target_current_setpoint_in_amps",
            "read_active_target_voltage_setpoint_in_volts",
            "read_active_target_arc_Detect_Delay_time_in_us",
            "read_active_target_arc_Off_time_in_us",
            "read_active_target_kilowatthour_Limit_in_kWh",
            "read_active_target_kilowatthour_count_in_kWh",
            "read_active_target_ramp_time_in_s",
            "read_active_target_run_time_in_s"
        ]:
            visible_action_name = func_name.replace("_", " ")

            bwe = ButtonWithEdits(visible_action_name, self.device, func_name, [], {})

            self.device_group.layout().addWidget(bwe)

        # Functions with parameters and simple responses
        for func_name in [
            "set_active_target_number",
            "set_heartbeat_timeout",
            "set_active_target_power_setpoint",
            "set_active_target_current_setpoint",
            "set_active_target_voltage_setpoint",
            "set_active_target_arc_detect_delay",
            "set_active_target_arc_off_time",
            "set_active_target_kwh_limit",
            "set_active_target_ramp_time",
            "set_active_target_run_time"
        ]:
            argspec = inspect.getfullargspec(getattr(PD500X1, func_name))
            args = argspec.args[1:]
            annotations = argspec.annotations

            visible_action_name = func_name.replace("_", " ")
            bwe = ButtonWithEdits(visible_action_name, self.device, func_name, args, annotations)

            self.device_group.layout().addWidget(bwe)

        for func_name in ["set_commands_help", "query_commands_help", "read_fault_bits", "read_status_bits"]:
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
        self.device = PD500X1(comport=self.comport_dropdown.currentText())
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
