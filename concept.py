from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from dotenv import load_dotenv
import os
import sys
sys.path.append('.')  # Ajoute le dossier courant au chemin de recherche
from openai import OpenAI

class ConceptTab(QWidget):
    concept_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_api_key()
        self.current_stream = None
        self.stream_buffer = ""
        self.load_system_prompt()
        self.client = None

    def initUI(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Chat area
        chat_layout = QVBoxLayout()
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        chat_layout.addWidget(self.chat_area)

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Envoyer")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        chat_layout.addLayout(input_layout)
        layout.addLayout(chat_layout)

        # Concept display area
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)

    def load_api_key(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            self.chat_area.append("Erreur : Clé API OpenAI non trouvée dans le fichier .env. Veuillez ajouter OPENAI_API_KEY à votre fichier .env.")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                self.chat_area.append(f"Erreur lors de l'initialisation du client OpenAI : {str(e)}")
                self.client = None

    def load_system_prompt(self):
        try:
            with open('prompts/concept.md', 'r', encoding='utf-8') as f:
                self.system_prompt = f.read()
        except FileNotFoundError:
            self.system_prompt = "Vous êtes un assistant créatif pour aider à développer des concepts de chansons."
            self.chat_area.append("Attention : Le fichier prompts/concept.md n'a pas été trouvé. Utilisation d'un prompt par défaut.")

    def send_message(self):
        user_message = self.input_field.text()
        self.chat_area.append(f"Vous : {user_message}")
        self.input_field.clear()

        if self.client is None:
            self.chat_area.append("Erreur : Le client OpenAI n'est pas initialisé. Veuillez vérifier votre clé API.")
            return

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            assistant_message = response.choices[0].message.content
            self.chat_area.append("Assistant : " + assistant_message)
            self.update_concept(assistant_message)
        except Exception as e:
            self.chat_area.append(f"Erreur lors de l'envoi du message : {str(e)}")
            self.chat_area.append("Veuillez vérifier votre connexion internet et la validité de votre clé API.")

    def update_concept(self, new_content):
        current_concept = self.result_area.toPlainText()
        updated_concept = current_concept + "\n\n" + new_content
        self.result_area.setPlainText(updated_concept)
        self.concept_updated.emit(updated_concept)
        
        # Sauvegarder le concept dans concept.md
        with open('concept.md', 'w', encoding='utf-8') as f:
            f.write(updated_concept)
