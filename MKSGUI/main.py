import sys
import logging
import traceback
from PyQt5.QtWidgets import QApplication
from gui.MainWindow import MainWindow


def expect_hook(x, y, z):
    traceback.print_exception(x, y, z)
    logging.debug(traceback.format_exception(x, y, z))


sys.excepthook = expect_hook
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log", mode="w"),
        logging.StreamHandler(sys.stdout)
    ]
)


def main():
    logging.debug("Setting up app")
    qapp = QApplication(sys.argv)
    gui = MainWindow()
    gui.show()
    logging.debug("Setting up app - done")
    gui.setMinimumSize(500, 500)
    sys.exit(qapp.exec_())

main()