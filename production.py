from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLineEdit
from PyQt5.QtCore import pyqtSignal

class ProductionTab(QWidget):
    production_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Zone de texte pour afficher les résultats
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)

        # Zone de saisie et bouton d'envoi
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.send_button = QPushButton("Envoyer")
        self.send_button.clicked.connect(self.on_send)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

    def on_send(self):
        # Ici, vous pouvez ajouter la logique pour traiter l'entrée de l'utilisateur
        user_input = self.input_field.text()
        self.result_area.append(f"Entrée utilisateur : {user_input}")
        self.input_field.clear()

    def update_production(self, new_content):
        current_content = self.result_area.toPlainText()
        updated_content = current_content + "\n\n" + new_content
        self.result_area.setPlainText(updated_content)
        self.production_updated.emit(updated_content)
