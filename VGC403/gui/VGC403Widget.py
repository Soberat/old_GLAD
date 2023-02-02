from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton, QLineEdit, QLabel, QHBoxLayout
from serial.tools.list_ports import comports

from driver.VGC403 import VGC403


class VGC403Widget(QWidget):
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
        self.interval_edit.setText("10")
        self.interval_edit.editingFinished.connect(self.update_interval)

        self.measurement_timer = QTimer()

        self.sensor_1_readout_label = QLabel("Sensor 1 readout: none")
        self.sensor_2_readout_label = QLabel("Sensor 2 readout: none")
        self.sensor_3_readout_label = QLabel("Sensor 3 readout: none")

        temp_layout = QHBoxLayout()

        temp_layout.addWidget(self.comport_dropdown)
        temp_layout.addWidget(QLabel("Interval"))
        temp_layout.addWidget(self.interval_edit)
        temp_layout.addWidget(QLabel("seconds"))
        temp_layout.addWidget(self.connect_button)

        self.layout().addLayout(temp_layout)

        self.layout().addWidget(self.sensor_1_readout_label)
        self.layout().addWidget(self.sensor_2_readout_label)
        self.layout().addWidget(self.sensor_3_readout_label)

    def connect_device(self):
        self.device = VGC403(comport=self.comport_dropdown.currentText())
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
        readouts = self.device.read_pressure_sensor(1), \
                   self.device.read_pressure_sensor(2), \
                   self.device.read_pressure_sensor(3)
        if readouts[0].status == 0:
            self.sensor_1_readout_label.setText(f"Sensor 1 readout: {readouts[0].value}e{readouts[0].error} mbar")
        else:
            self.sensor_1_readout_label.setText(f"Sensor 1 readout: {self.device.get_pr_status_string(readouts[0].status)}")
        if readouts[1].status == 0:
            self.sensor_2_readout_label.setText(f"Sensor 2 readout: {readouts[1].value}e{readouts[1].error} mbar")
        else:
            self.sensor_2_readout_label.setText(f"Sensor 2 readout: {self.device.get_pr_status_string(readouts[1].status)}")
        if readouts[2].status == 0:
            self.sensor_3_readout_label.setText(f"Sensor 3 readout: {readouts[2].value}e{readouts[2].error} mbar")
        else:
            self.sensor_3_readout_label.setText(f"Sensor 3 readout: {self.device.get_pr_status_string(readouts[2].status)}")

    def update_interval(self):
        if self.device:
            self.measurement_timer.start(int(1000 * float(self.interval_edit.text().replace(",", "."))))
