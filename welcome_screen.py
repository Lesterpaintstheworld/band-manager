import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class WelcomeScreen(QWidget):
    submitted = pyqtSignal()

    def __init__(self, change_name=False):
        super().__init__()
        self.change_name = change_name
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Band Manager')
        self.showFullScreen()

        layout = QVBoxLayout()
        self.setLayout(layout)

        if self.change_name:
            welcome_label = QLabel("Change Band Name")
        else:
            welcome_label = QLabel("Welcome to Band Manager")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setFont(QFont('Arial', 32, QFont.Bold))
        welcome_label.setStyleSheet("color: #ff0000;")
        layout.addWidget(welcome_label)

        choose_label = QLabel("Choose your band name:")
        choose_label.setAlignment(Qt.AlignCenter)
        choose_label.setFont(QFont('Arial', 24))
        layout.addWidget(choose_label)

        self.name_input = QLineEdit()
        self.name_input.setFont(QFont('Arial', 18))
        self.name_input.setFixedWidth(400)
        layout.addWidget(self.name_input, alignment=Qt.AlignCenter)

        submit_button = QPushButton("Submit")
        submit_button.setFont(QFont('Arial', 18))
        submit_button.setFixedWidth(200)
        submit_button.clicked.connect(self.save_band_name)
        layout.addWidget(submit_button)

    def save_band_name(self):
        band_name = self.name_input.text()
        if band_name:
            with open('band.json', 'w') as f:
                json.dump({"name": band_name, "fans": 0}, f)
            self.submitted.emit()
