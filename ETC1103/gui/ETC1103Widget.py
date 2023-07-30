import serial.tools.list_ports
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton, QGroupBox, QLabel, QHBoxLayout

from driver.ETC1103 import ETC1103


class ETC1103Widget(QWidget):
    def __init__(self):
        super().__init__()

        self._device = None
        self.device_update_timer = QTimer()
        self.device_update_timer.timeout.connect(self.get_device_info)

        self.setLayout(QVBoxLayout())

        self.comport_dropdown = QComboBox()
        self.comport_dropdown.addItems([d.name for d in serial.tools.list_ports.comports()])

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_device)

        self.device_groupbox = QGroupBox()
        self.device_groupbox.setLayout(QVBoxLayout())

        self.status_label = QLabel("Status: unknown")
        self.operational_time_label = QLabel("Operational time: unknown")
        self.output_frequency_label = QLabel("Output frequency: unknown")
        self.failure_details_label = QLabel("Failures: normal")

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")

        self.device_groupbox.layout().addWidget(self.status_label)
        self.device_groupbox.layout().addWidget(self.operational_time_label)
        self.device_groupbox.layout().addWidget(self.output_frequency_label)
        self.device_groupbox.layout().addWidget(self.failure_details_label)

        temp_layout = QHBoxLayout()

        temp_layout.addWidget(self.start_button)
        temp_layout.addWidget(self.stop_button)

        self.device_groupbox.layout().addLayout(temp_layout)

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.comport_dropdown)
        temp_layout.addWidget(self.connect_button)

        self.layout().addLayout(temp_layout)
        self.layout().addWidget(self.device_groupbox)

    def connect_device(self):
        self._device = ETC1103(comport=self.comport_dropdown.currentText())

        self.connect_button.setText("Disconnect")
        self.connect_button.clicked.disconnect()
        self.connect_button.clicked.connect(self.disconnect_device)
        self.comport_dropdown.setEnabled(False)

        self.start_button.clicked.connect(self._device.start_pump)
        self.stop_button.clicked.connect(self._device.stop_pump)

        self.device_groupbox.setEnabled(True)

        self.device_update_timer.start(2000)

    def disconnect_device(self):
        self._device = None

        self.connect_button.setText("Connect")
        self.connect_button.clicked.disconnect()
        self.connect_button.clicked.connect(self.connect_device)
        self.comport_dropdown.setEnabled(True)

        self.start_button.clicked.disconnect()
        self.stop_button.clicked.disconnect()

        self.device_groupbox.setEnabled(False)

        self.device_update_timer.stop()

    def get_device_info(self):
        self.status_label.setText(f"Status: {self._device.get_pump_status()}")
        self.operational_time_label.setText(f"Operational time: {self._device.get_operational_time()} h")
        self.output_frequency_label.setText(f"Output frequency: {self._device.get_output_frequency()} h")
        self.failure_details_label.setText(f"Failures: {self._device.get_failure_details()}")
