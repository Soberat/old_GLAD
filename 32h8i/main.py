from PyQt5.QtWidgets import *

from gui.Q32h8iWidget import Q32h8iWidget

app = QApplication([])
label = Q32h8iWidget()
label.show()
app.exec()