from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QHBoxLayout


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

    def add_new_line(self, widgets: list):
        layout = QHBoxLayout()
        for w in widgets:
            layout.addWidget(w)
        layout.addStretch(0)
        self.layout().addLayout(layout)

