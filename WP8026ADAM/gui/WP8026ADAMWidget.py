from typing import Iterable

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QComboBox, QPushButton, QLineEdit, QLabel, QHBoxLayout, QVBoxLayout
from serial.tools.list_ports import comports

from driver.WP8026ADAM import WP8026ADAM


class WP8026ADAMWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.device = None

        self.setLayout(QVBoxLayout())

        self.comport_dropdown = QComboBox()
        self.comport_dropdown.addItems([comport.name for comport in comports()])

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_device)

        self.interval_edit = QLineEdit()
        self.interval_edit.setValidator(QDoubleValidator())
        self.interval_edit.setText("2")
        self.interval_edit.editingFinished.connect(self.update_interval)

        self.measurement_timer = QTimer()

        self.input_readout_labels: Iterable[QLabel] = [QLabel(f"Input {i}: UNKNOWN") for i in range(1, 17)]

        temp_layout = QHBoxLayout()

        temp_layout.addWidget(self.comport_dropdown)
        temp_layout.addWidget(QLabel("Interval"))
        temp_layout.addWidget(self.interval_edit)
        temp_layout.addWidget(QLabel("seconds"))
        temp_layout.addWidget(self.connect_button)

        self.layout().addLayout(temp_layout)

        for label in self.input_readout_labels:
            self.layout().addWidget(label)

    def connect_device(self):
        self.device = WP8026ADAM(comport=self.comport_dropdown.currentText())
        self.measurement_timer.timeout.connect(self.get_measurements)
        self.measurement_timer.start(1000 * int(self.interval_edit.text()))
        self.connect_button.setText("Disconnect")
        self.connect_button.clicked.disconnect(self.connect_device)
        self.connect_button.clicked.connect(self.disconnect_device)

    def disconnect_device(self):
        self.device = None
        self.measurement_timer.timeout.disconnect(self.get_measurements)
        self.measurement_timer.stop()
        self.connect_button.setText("Connect")
        self.connect_button.clicked.disconnect(self.disconnect_device)
        self.connect_button.clicked.connect(self.connect_device)

    def get_measurements(self):
        assert self.device, "There was no device, but measurements were requested"
        readouts = self.device.get_input_states()

        for idx, label in enumerate(self.input_readout_labels):
            label.setText(f"Input {idx+1}: {readouts[idx].name}")

    def update_interval(self):
        if self.device:
            self.measurement_timer.start(int(1000 * float(self.interval_edit.text().replace(",", "."))))
