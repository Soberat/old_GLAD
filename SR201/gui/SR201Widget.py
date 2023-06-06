from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from ipaddress import IPv4Address
from driver.SR201 import SR201, RelayState


class SR201Widget(QWidget):
    def __init__(self, ipv4_address: IPv4Address):
        super().__init__()

        self.device = SR201(ipv4_address)

        self.setLayout(QVBoxLayout())

        # Create two horizontal layouts for 2 rows of relays
        l1 = QHBoxLayout()
        l2 = QHBoxLayout()

        # Add the two horizontal layouts to the main layout
        self.layout().addLayout(l1)
        self.layout().addLayout(l2)
        # Create a widget for every relay for the device
        for channel in range(0, 16):
            if channel <= 7:
                l1.addWidget(self._create_channel_widget(channel))
            else:
                l2.addWidget(self._create_channel_widget(channel))

        self.device.get_relay_states()

    def _create_channel_widget(self, channel_n: int):
        widget = QWidget()
        widget.setLayout(QVBoxLayout())

        widget.layout().addWidget(QLabel(f"Channel {channel_n}"))

        # Add a state label
        label = QLabel()

        def f(relay_n: int, state: RelayState):
            if not relay_n == channel_n:
                return

            if state == RelayState.OPEN:
                label.setPixmap(QPixmap("./res/button_green.png").scaled(32, 32, transformMode=Qt.SmoothTransformation))
            elif state == RelayState.CLOSED:
                label.setPixmap(QPixmap("./res/button_red.png").scaled(32, 32, transformMode=Qt.SmoothTransformation))
            else:
                label.setPixmap(QPixmap(""))

        self.device.stateChanged.connect(f)
        widget.layout().addWidget(label)

        # Add 2 QPushButton widgets in a horizontal layout
        open_button = QPushButton("Open")
        open_button.clicked.connect(lambda: self.device.set_relay_state(channel_n, RelayState.OPEN))
        close_button = QPushButton("Close")
        close_button.clicked.connect(lambda: self.device.set_relay_state(channel_n, RelayState.CLOSED))

        temp_layout = QHBoxLayout()
        temp_layout.addWidget(open_button)
        temp_layout.addWidget(close_button)
        widget.layout().addLayout(temp_layout)

        return widget