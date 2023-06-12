# This is a sample Python script.
import logging
import sys

from PyQt5.QtWidgets import QApplication, QScrollArea

from gui.RX01Widget import RX01Widget

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                        datefmt='%H:%M:%S')

    app = QApplication([])

    window = RX01Widget()
    scroll_area = QScrollArea()
    scroll_area.setWidget(window)

    scroll_area.show()

    sys.exit(app.exec())
