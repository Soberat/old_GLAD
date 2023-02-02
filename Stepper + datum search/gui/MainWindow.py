import logging
import time

from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QMainWindow, QPushButton, QScrollArea, QLineEdit, QGroupBox, QVBoxLayout, QLabel
import inspect
from driver.StepperController import StepperController, StepperControllerAxis
from gui.ButtonWithEdits import ButtonWithEdits
from gui.CentralWidget import CentralWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        widget = CentralWidget()
        stepper = StepperController(comport="COM3")
        self.axisX = StepperControllerAxis(stepper, 1)

        datum_search_group = QGroupBox()
        temp_layout = QVBoxLayout()

        initial_speed_edit = QLineEdit()
        initial_speed_edit.setPlaceholderText("Prędkość pierwszego podejścia do hard limitu")
        initial_speed_edit.setValidator(QIntValidator())
        temp_layout.addWidget(initial_speed_edit)

        shift_edit = QLineEdit()
        shift_edit.setPlaceholderText("Przesunięcie w krokach po osiągnięciu hard limitu")
        shift_edit.setValidator(QIntValidator())
        temp_layout.addWidget(shift_edit)

        creep_speed_edit = QLineEdit()
        creep_speed_edit.setPlaceholderText("Prędkość drugiego podejścia do hard limitu")
        creep_speed_edit.setValidator(QIntValidator())
        temp_layout.addWidget(creep_speed_edit)

        search_routine_execution_button = QPushButton()
        search_routine_execution_button.setText("Start")
        search_routine_execution_button.clicked.connect(lambda: self.start_search_routine(int(initial_speed_edit.text()),
                                                                                          int(shift_edit.text()),
                                                                                          int(creep_speed_edit.text())))
        temp_layout.addWidget(search_routine_execution_button)

        self.info_label = QLabel("Status: brak")
        temp_layout.addWidget(self.info_label)

        datum_search_group.setLayout(temp_layout)
        datum_search_group.setMaximumWidth(450)
        widget.layout().addWidget(datum_search_group)
        for func in [method_name for method_name in dir(self.axisX)
                     if callable(getattr(self.axisX, method_name)) and not method_name.startswith("_")]:
            combo = ButtonWithEdits(func, self.axisX, getattr(self.axisX, func),
                                    inspect.getfullargspec(getattr(self.axisX, func)).args[1:])
            widget.add_new_line([combo])

        sa = QScrollArea()
        sa.setWidget(widget)
        self.setCentralWidget(sa)
        self.setMinimumSize(500, 500)

    def start_search_routine(self, init_speed: int, shift_steps: int, creep_speed: int):
        # Krok 1
        self.info_label.setText("Krok 1: szybki home to datum")
        self.axisX.set_velocity(init_speed)
        self.axisX.go_home_to_datum(False)
        current_operation = self.axisX.display_current_operation()
        logging.debug("Current operation: {}".format(current_operation))
        while b"home" in current_operation.lower() or b"datum" in current_operation.lower():
            time.sleep(1)
            current_operation = self.axisX.display_current_operation()
            logging.debug("Current operation: {}".format(current_operation))

        # Liczba kroków od której kontroler wykorzystuje creep speed zamiast slew speed
        self.axisX.set_creep_steps(shift_steps)
        self.axisX.set_creep_speed(creep_speed)
        # Krok 2
        self.info_label.setText("Krok 2: odsunięcie od hard limitu")
        self.axisX.move_relative(-shift_steps)

        current_operation = self.axisX.display_current_operation()
        logging.debug("Current operation: {}".format(current_operation))
        while b"idle" not in current_operation.lower():
            time.sleep(1)
            current_operation = self.axisX.display_current_operation()
            logging.debug("Current operation: {}".format(current_operation))

        # Krok 3
        self.info_label.setText("Krok 3: wolny home to datum")
        self.axisX.go_home_to_datum(False)
        # self.axisX.constant_velocity_move(creep_speed)
        self.info_label.setText("Koniec")


