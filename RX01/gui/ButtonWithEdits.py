from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QHBoxLayout, QLabel


class ButtonWithEdits(QWidget):
    def __init__(self, button_text, target, func_name, args, annotations, output_class=QLabel):
        super().__init__()

        self.setLayout(QHBoxLayout())

        self.button = QPushButton(button_text)
        self.button.setFixedWidth(200)
        self.layout().addWidget(self.button)

        self.func_name = func_name
        self.target = target
        self.annotations = annotations
        self.edits = []

        for arg in args:
            edit = QLineEdit()
            edit.setPlaceholderText(arg)
            edit.setFixedWidth(300)
            self.edits.append(edit)
            self.layout().addWidget(edit)

        self.output = output_class()
        self.layout().addWidget(self.output)

        self.clear_timer = QTimer()

        self.button.clicked.connect(self.funci)

        self.layout().addStretch(0)

    def funci(self):
        func = getattr(self.target, self.func_name)
        response = func(**self.get_args_from_edits())
        self.output.setText(f"Response: {response}")

        # Timer to clear text after 5 seconds
        timer = QTimer()
        timer.singleShot(5000, lambda: self.output.setText(""))

    def get_args_from_edits(self):
        argos = {}
        for edit in self.edits:
            # cast as proper type
            argos[edit.placeholderText()] = self.annotations[edit.placeholderText()](edit.text())

        return argos