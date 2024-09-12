from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import os
from openai import OpenAI

class ManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_system_prompt()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Zone de texte pour afficher les informations du groupe
        self.info_area = QTextEdit()
        self.info_area.setReadOnly(True)
        layout.addWidget(self.info_area)

        # Zone de chat
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.append("Welcome to the Management Tab! Here you can manage your band's information and strategy. Use the input field below to ask questions or make decisions about your band's management.")
        layout.addWidget(self.chat_area)

        # Champ de saisie pour les nouvelles informations
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.send_message)
        layout.addWidget(self.input_field)

        # Bouton pour envoyer le message
        self.send_button = QPushButton("Envoyer")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        # Bouton pour mettre à jour les informations du groupe
        self.update_button = QPushButton("Mettre à jour les informations du groupe")
        self.update_button.clicked.connect(self.update_info)
        layout.addWidget(self.update_button)

        # Charger les informations existantes
        self.load_info()

    def load_system_prompt(self):
        try:
            with open('prompts/management.md', 'r', encoding='utf-8') as f:
                self.system_prompt = f.read().strip()
        except FileNotFoundError:
            self.system_prompt = "You are a helpful assistant for band management."

    def load_info(self):
        try:
            with open('band_info.txt', 'r', encoding='utf-8') as f:
                info = f.read()
            self.info_area.setPlainText(info)
        except FileNotFoundError:
            info = "Nom du groupe : The Rockers\nStyle : Rock alternatif\nObjectif : Devenir le meilleur groupe de rock du monde"
            self.info_area.setPlainText(info)

    def send_message(self):
        user_message = self.input_field.text()
        self.chat_area.append(f"Vous : {user_message}")
        self.input_field.clear()

        try:
            self.chat_area.append("Assistant : ")
            for chunk in self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                stream=True
            ):
                if chunk.choices[0].delta.content is not None:
                    self.chat_area.insertPlainText(chunk.choices[0].delta.content)
                    QApplication.processEvents()
        except Exception as e:
            self.chat_area.append(f"Erreur : {str(e)}")

    def update_info(self):
        current_info = self.info_area.toPlainText()
        with open('band_info.txt', 'w', encoding='utf-8') as f:
            f.write(current_info)
        
        # Mise à jour du fichier management.md
        with open('management.md', 'w', encoding='utf-8') as f:
            f.write(current_info)
        
        self.chat_area.append("Informations du groupe mises à jour et sauvegardées dans band_info.txt et management.md.")
