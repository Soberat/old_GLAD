import sys

from PyQt5.QtWidgets import QApplication

from gui.WP8026ADAMWidget import WP8026ADAMWidget

if __name__ == '__main__':
    app = QApplication([])
    widget = WP8026ADAMWidget()

    widget.show()

    sys.exit(app.exec())
