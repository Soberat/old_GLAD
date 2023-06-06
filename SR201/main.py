from ipaddress import IPv4Address

from PyQt5.QtWidgets import QApplication

from gui.SR201Widget import SR201Widget

if __name__ == '__main__':
    app = QApplication([])
    widget = SR201Widget(IPv4Address("192.168.1.100"))
    widget.show()
    app.exec_()