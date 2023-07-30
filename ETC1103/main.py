import sys

from PyQt5.QtWidgets import QApplication

from gui.ETC1103Widget import ETC1103Widget

if __name__ == '__main__':
    app = QApplication([])
    window = ETC1103Widget()

    window.show()

    sys.exit(app.exec())