from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QObject, pyqtSlot
from dotenv import load_dotenv
import os
import sys
sys.path.append('.')  # Ajoute le dossier courant au chemin de recherche
from openai import OpenAI
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

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
        self.load_initial_composition()

    def load_initial_composition(self):
        try:
            with open('composition.md', 'r', encoding='utf-8') as f:
                initial_composition = f.read()
            self.result_area.setPlainText(initial_composition)
        except FileNotFoundError:
            self.chat_area.append("Warning: composition.md file not found. Starting with an empty composition.")

    def initUI(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Chat area
        chat_layout = QVBoxLayout()
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.textChanged.connect(lambda: self.chat_area.ensureCursorVisible())
        self.chat_area.append("Greetings! I'm Rhythm, your composition companion. Welcome to the Composition Tab! Here you can work on the musical composition of your song. Start by describing your ideas for the melody, harmony, or overall structure in the input field below.")
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
        self.result_area.textChanged.connect(self.save_composition)
        self.result_area.textChanged.connect(lambda: self.result_area.ensureCursorVisible())
        layout.addWidget(self.result_area)

    def save_composition(self):
        with open('composition.md', 'w', encoding='utf-8') as f:
            f.write(self.result_area.toPlainText())

    def load_api_key(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            print("Error: OpenAI API key not found in .env file. Please add OPENAI_API_KEY to your .env file.")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.client.models.list()  # Test the client to ensure it's working
            except Exception as e:
                print(f"Error initializing OpenAI client: {str(e)}")
                print("Please check your API key in the .env file")
                self.client = None

    def load_system_prompt(self):
        try:
            composition_prompt = self.read_file(resource_path('prompts/composition.md'))
            concept_content = self.read_file(resource_path('concept.md'))
            lyrics_content = self.read_file(resource_path('lyrics.md'))
            production_content = self.read_file(resource_path('production.md'))
            
            self.system_prompt = f"{composition_prompt}\n\nContext from concept.md:\n{concept_content}\n\nContext from lyrics.md:\n{lyrics_content}\n\nContext from production.md:\n{production_content}"
        except Exception as e:
            self.system_prompt = "You are a creative assistant to help compose music."
            self.chat_area.append(f"Warning: Error loading prompts: {str(e)}. Using a default prompt.")

    def read_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"File {filepath} not found."

    def send_message(self):
        # Update the system prompt with the latest content
        self.load_system_prompt()
        
        user_message = self.input_field.text()

    def send_message(self):
        # Update the system prompt with the latest content
        self.load_system_prompt()
        
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
            self.chat_area.append("Assistant : ")
            
            # Read content from relevant files
            concept_content = self.read_file(resource_path('concept.md'))
            lyrics_content = self.read_file(resource_path('lyrics.md'))
            production_content = self.read_file(resource_path('production.md'))
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": f"Concept:\n{concept_content}"},
                {"role": "system", "content": f"Lyrics:\n{lyrics_content}"},
                {"role": "system", "content": f"Production:\n{production_content}"},
                {"role": "user", "content": user_message}
            ]
            
            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
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
