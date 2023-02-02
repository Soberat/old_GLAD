from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QHBoxLayout


class ButtonWithEdits(QWidget):
    def __init__(self, button_text, target, func, edits):
        super().__init__()

        self.setLayout(QHBoxLayout())

        self.button = QPushButton(button_text)
        self.button.setFixedWidth(200)
        self.layout().addWidget(self.button)

        self.func = func
        self.target = target
        self.edits = []

        for arg in edits:
            edit = QLineEdit()
            edit.setPlaceholderText(arg)
            edit.setFixedWidth(150)
            self.edits.append(edit)
            self.layout().addWidget(edit)

        self.button.clicked.connect(self.funci)

        self.layout().addStretch(0)

    def funci(self):
        self.func(**self.get_args_from_edits())

    def get_args_from_edits(self):
        argos = {}
        for edit in self.edits:
            argos[edit.placeholderText()] = edit.text()

        return argos