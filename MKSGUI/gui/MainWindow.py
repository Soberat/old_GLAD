import logging

from PyQt5.QtWidgets import QMainWindow, QGridLayout

from gui.MksEthWidget import MksEthWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logging.debug("Init MainWindow")
        self.setCentralWidget(MksEthWidget("192.168.2.155"))
