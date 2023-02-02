from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QWidget, QLineEdit, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, \
    QSpinBox, QDoubleSpinBox
from serial.tools.list_ports import comports

from driver.TempController32h8i import TempController32h8i


class Q32h8iWidget(QWidget):
    def __init__(self):
        super(Q32h8iWidget, self).__init__()
        self.device: TempController32h8i = None

        self.setLayout(QVBoxLayout())

        self.slave_address_input = QLineEdit()
        self.slave_address_input.setValidator(QIntValidator())
        self.slave_address_input.setPlaceholderText("Slave address")

        self.comport_dropdown = QComboBox()
        self.comport_dropdown.addItems([device.name for device in comports()])

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_device)

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.slave_address_input)
        temp_layout.addWidget(self.comport_dropdown)
        temp_layout.addWidget(self.connect_button)
        self.layout().addLayout(temp_layout)

        self.actions_group = QGroupBox()
        self.actions_group.setEnabled(False)
        self.actions_group.setLayout(QVBoxLayout())

        self.temperature_readout_label = QLabel("Temperature: None ℃")
        self.temperature_readout_timer = QTimer()

        self.setpoint_spinbox = QDoubleSpinBox()
        self.process_value_spinbox = QDoubleSpinBox()

        self.actions_group.layout().addWidget(self.temperature_readout_label)

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Setpoint "))
        temp_layout.addWidget(self.setpoint_spinbox)
        temp_layout.addStretch(0)
        self.actions_group.layout().addLayout(temp_layout)

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Process value "))
        temp_layout.addWidget(self.process_value_spinbox)
        temp_layout.addStretch(0)
        self.actions_group.layout().addLayout(temp_layout)

        self.layout().addWidget(self.actions_group)
        self.layout().addStretch(0)

    def connect_to_device(self):
        self.device = TempController32h8i(int(self.slave_address_input.text()),
                                          self.comport_dropdown.currentText())
        if self.device:
            self.actions_group.setEnabled(True)
            self.setpoint_spinbox.valueChanged.connect(self.device.set_setpoint_value)
            self.temperature_readout_timer.timeout.connect(
                lambda: self.temperature_readout_label.setText("Temperature: "
                                                               f"{self.device.get_process_value(is_comms_value=False)}"
                                                               " ℃"))
            self.process_value_spinbox.valueChanged.connect(
                lambda val: self.device.set_process_value(val, is_comms_value=True))
            self.temperature_readout_timer.start(10000)
            self.connect_button.setText("Disconnect")
            self.connect_button.clicked.disconnect()
            self.connect_button.clicked.connect(self.disconnect_device)

    def disconnect_device(self):
        self.device = None
        self.actions_group.setEnabled(False)
        self.setpoint_spinbox.valueChanged.disconnect()
        self.temperature_readout_timer.timeout.disconnect()
        self.process_value_spinbox.valueChanged.disconnect()
        self.temperature_readout_timer.stop()
        self.connect_button.setText("Connect")
        self.connect_button.clicked.disconnect()
        self.connect_button.clicked.connect(self.connect_to_device)
