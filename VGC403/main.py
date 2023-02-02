# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import logging
import sys

from PyQt5.QtWidgets import QApplication

from driver.VGC403 import VGC403


# Press the green button in the gutter to run the script.
from gui.MainWindow import MainWindow

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("debug.log", mode="w"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    app = QApplication([])
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec_())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
