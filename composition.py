from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QObject, pyqtSlot
from dotenv import load_dotenv
import os
import sys
sys.path.append('.')  # Ajoute le dossier courant au chemin de recherche
from openai import OpenAI

class CompositionTab(QWidget):
    composition_updated = pyqtSignal(str)

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

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        chat_layout.addLayout(input_layout)
        layout.addLayout(chat_layout)

        # Composition display area
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)

    def load_api_key(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            self.chat_area.append("Error: OpenAI API key not found in .env file. Please add OPENAI_API_KEY to your .env file.")
            self.client = None
        else:
            # Afficher les premiers et derniers caractères de la clé API
            masked_key = f"{self.api_key[:5]}...{self.api_key[-5:]}"
            self.chat_area.append(f"API key found: {masked_key}")
            try:
                self.client = OpenAI(api_key=self.api_key)
                # Test the client to ensure it's working
                self.client.models.list()
                self.chat_area.append("OpenAI client initialized successfully.")
            except Exception as e:
                self.chat_area.append(f"Error initializing OpenAI client: {str(e)}")
                self.chat_area.append("Please check your API key in the .env file")
                self.client = None

    def load_system_prompt(self):
        try:
            with open('prompts/composition.md', 'r', encoding='utf-8') as f:
                composition_prompt = f.read()
            
            with open('concept.md', 'r', encoding='utf-8') as f:
                concept_content = f.read()
            
            with open('lyrics.md', 'r', encoding='utf-8') as f:
                lyrics_content = f.read()
            
            self.system_prompt = f"{composition_prompt}\n\nContext from concept.md:\n{concept_content}\n\nContext from lyrics.md:\n{lyrics_content}"
        except FileNotFoundError as e:
            self.system_prompt = "You are a creative assistant to help compose music."
            self.chat_area.append(f"Warning: File not found: {str(e)}. Using a default prompt.")

    def send_message(self):
        user_message = self.input_field.text()
        self.chat_area.append(f"You: {user_message}")
        self.input_field.clear()

        if not self.api_key:
            self.chat_area.append("Error: OpenAI API key not found. Please check your .env file.")
            return

        if self.client is None:
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.chat_area.append("OpenAI client reinitialized successfully.")
            except Exception as e:
                self.chat_area.append(f"Error reinitializing OpenAI client: {str(e)}")
                return

        try:
            self.stream_buffer = ""
            self.chat_area.append("Assistant: ")
            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    self.stream_buffer += chunk.choices[0].delta.content
                    self.chat_area.insertPlainText(chunk.choices[0].delta.content)
                    QApplication.processEvents()
            self.update_composition(self.stream_buffer)
        except Exception as e:
            self.chat_area.append(f"Error sending message: {str(e)}")
            self.chat_area.append("Please check your internet connection and the validity of your API key.")

    def update_composition(self, new_content):
        current_composition = self.result_area.toPlainText()
        updated_composition = current_composition + "\n\n" + new_content
        self.result_area.setPlainText(updated_composition)
        self.composition_updated.emit(updated_composition)
        
        # Sauvegarder la composition dans composition.md
        with open('composition.md', 'w', encoding='utf-8') as f:
            f.write(updated_composition)
