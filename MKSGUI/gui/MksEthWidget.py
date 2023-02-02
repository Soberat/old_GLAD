import random
from datetime import datetime, timedelta
import logging
import pyqtgraph
from PyQt5.QtCore import QTimer, QThreadPool, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QDoubleSpinBox, QGroupBox, QRadioButton, QHBoxLayout, \
    QLineEdit
from pyqtgraph import PlotWidget, DateAxisItem
from driver.MksEthMfc import MksEthMfc, MksEthMfcWorker, MksEthMfcWorkerTask, MksEthMfcValveState


# TODO: Query current valve state before ending __init__

class MksEthWidget(QWidget):
    def __init__(self, ip_address: str):
        logging.debug("Setting up MksEthWidget with ip {}".format(ip_address))
        super().__init__()

        self.setLayout(QVBoxLayout())

        self.mks_mfc = MksEthMfc(ip_address)
        self.mks_mfc_async_worker = MksEthMfcWorker()
        self.thread_pool = QThreadPool.globalInstance()
        self.thread_pool.start(self.mks_mfc_async_worker)
        self.mks_mfc_async_worker.signals.flow_ready.connect(self.update_widget)

        self.sampling_timer = QTimer()
        self.sampling_timer.timeout.connect(lambda: self.mks_mfc_async_worker.task_queue.put(
            MksEthMfcWorkerTask(self.mks_mfc_async_worker.signals.flow_ready,
                                lambda: self.mks_mfc.get_flow(),
                                -1)))
        self.sampling_timer.start(1000)

        self.sample_buffer = list()
        self.timestamp_buffer = list()

        self.info_label = QLabel("Brak błędów")
        self.ip_address_label = QLabel("Adres IP: {}".format(ip_address))
        self.setpoint_spinbox = QDoubleSpinBox()
        self.setpoint_spinbox.valueChanged.connect(lambda val: self.mks_mfc_async_worker.task_queue.put(
            MksEthMfcWorkerTask(self.mks_mfc_async_worker.signals.empty,
                                lambda: self.mks_mfc.set_setpoint(val),
                                False)))
        self.plot_widget = PlotWidget()
        self.valve_state_group = QGroupBox("Tryb zaworu")
        self.valve_normal_button = QRadioButton("Normalny")
        self.valve_normal_button.clicked.connect(lambda: self.mks_mfc_async_worker.task_queue.put(
            MksEthMfcWorkerTask(self.mks_mfc_async_worker.signals.empty,
                                lambda: self.mks_mfc.set_valve_state(MksEthMfcValveState.NORMAL),
                                False)))
        self.valve_closed_button = QRadioButton("Zamknięty")
        self.valve_closed_button.clicked.connect(lambda: self.mks_mfc_async_worker.task_queue.put(
            MksEthMfcWorkerTask(self.mks_mfc_async_worker.signals.empty,
                                lambda: self.mks_mfc.set_valve_state(MksEthMfcValveState.CLOSED),
                                False)))
        self.valve_open_button = QRadioButton("Otwarty")
        self.valve_open_button.clicked.connect(lambda: self.mks_mfc_async_worker.task_queue.put(
            MksEthMfcWorkerTask(self.mks_mfc_async_worker.signals.empty,
                                lambda: self.mks_mfc.set_valve_state(MksEthMfcValveState.OPEN),
                                False)))

        self.plot_widget.getPlotItem().showGrid(x=True, y=True, alpha=1)
        self.plot_widget.getPlotItem().setAxisItems(axisItems={"bottom": DateAxisItem()})

        self.intervalEdit = QLineEdit()
        self.intervalEdit.setText("1")
        self.intervalEdit.setValidator(QRegExpValidator(QRegExp("[0-9]*(|\\.[0-9]*)")))
        self.intervalEdit.editingFinished.connect(lambda: self.sampling_timer.setInterval(
                                                          int(float(self.intervalEdit.text()) * 60 * 1000)))
        self.intervalEdit.setMaximumWidth(150)

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.ip_address_label)
        self.layout().addLayout(temp_layout)

        self.layout().addWidget(self.info_label)

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.plot_widget)
        temp_layout.addWidget(self.setpoint_spinbox)
        self.layout().addLayout(temp_layout)

        temp_layout = QVBoxLayout()
        temp_layout.addWidget(self.valve_normal_button)
        temp_layout.addWidget(self.valve_closed_button)
        temp_layout.addWidget(self.valve_open_button)
        self.valve_state_group.setLayout(temp_layout)

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.valve_state_group)
        temp_layout.addWidget(QLabel("Interwał"))
        temp_layout.addWidget(self.intervalEdit)
        temp_layout.addWidget(QLabel(" minut"))
        temp_layout.addStretch(100)

        self.layout().addLayout(temp_layout)

    def update_widget(self, new_sample):
        if new_sample and new_sample != -1:
            logging.debug("New sample: {}".format(new_sample))
            self.sample_buffer.append(new_sample)
            self.timestamp_buffer.append(datetime(1, 1, 1).now().timestamp())

            self.plot_widget.clear()
            self.plot_widget.plot(x=self.timestamp_buffer,
                                  y=self.sample_buffer,
                                  pen=pyqtgraph.mkPen((255, 127, 0), width=1.25),
                                  symbolBrush=(255, 127, 0),
                                  symbolPen=pyqtgraph.mkPen((255, 127, 0)),
                                  symbol='o',
                                  symbolSize=5,
                                  name="symbol ='o'")

        else:
            logging.info("No new sample")
