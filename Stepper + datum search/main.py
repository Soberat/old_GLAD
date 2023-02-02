import logging
import sys

from PyQt5.QtWidgets import QApplication

from gui.MainWindow import MainWindow

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log", mode="w"),
        logging.StreamHandler(sys.stdout)
    ]
)


if __name__ == '__main__':
    logging.debug("Setting up app")
    qapp = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    logging.debug("Setting up app - done")
    sys.exit(qapp.exec_())
