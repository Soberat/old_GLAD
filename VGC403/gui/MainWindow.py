from PyQt5.QtWidgets import QMainWindow

from gui.VGC403Widget import VGC403Widget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setCentralWidget(VGC403Widget())