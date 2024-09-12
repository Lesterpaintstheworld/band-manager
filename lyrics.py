from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QApplication, QMenuBar, QAction, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QObject, pyqtSlot
import json
from dotenv import load_dotenv
import os
import sys
sys.path.append('.')  # Ajoute le dossier courant au chemin de recherche
from openai import OpenAI
from main import resource_path

class LyricsTab(QWidget):
    lyrics_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_api_key()
        self.current_stream = None
        self.stream_buffer = ""
        self.load_system_prompt()
        self.client = None
        self.load_initial_lyrics()

    def load_initial_lyrics(self):
        try:
            with open('lyrics.md', 'r', encoding='utf-8') as f:
                initial_lyrics = f.read()
            self.result_area.setPlainText(initial_lyrics)
        except FileNotFoundError:
            self.chat_area.append("Warning: lyrics.md file not found. Starting with empty lyrics.")

    def initUI(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Chat area
        chat_layout = QVBoxLayout()
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.textChanged.connect(lambda: self.chat_area.ensureCursorVisible())
        self.chat_area.append("Welcome to the Lyrics Tab! Here you can create and edit your song lyrics. Start by entering your ideas for lyrics or ask for suggestions in the input field below.")
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

        # Lyrics display area
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.result_area.textChanged.connect(lambda: self.result_area.ensureCursorVisible())
        layout.addWidget(self.result_area)

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
            lyrics_prompt = self.read_file(resource_path('prompts/lyrics.md'))
            concept_content = self.read_file(resource_path('concept.md'))
            composition_content = self.read_file(resource_path('composition.md'))
            
            self.system_prompt = f"{lyrics_prompt}\n\nContext from concept.md:\n{concept_content}\n\nContext from composition.md:\n{composition_content}"
        except Exception as e:
            self.system_prompt = "You are a creative assistant to help write song lyrics."
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
            # Read content from relevant files
            lyrics_prompt = self.read_file(resource_path('prompts/lyrics.md'))
            concept_content = self.read_file(resource_path('concept.md'))
            composition_content = self.read_file(resource_path('composition.md'))
            management_content = self.read_file(resource_path('management.md'))

            self.stream_buffer = ""
            self.chat_area.append("Assistant : ")
            
            # Generate title
            title_stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": lyrics_prompt},
                    {"role": "system", "content": f"Concept:\n{concept_content}"},
                    {"role": "system", "content": f"Composition:\n{composition_content}"},
                    {"role": "system", "content": f"Management:\n{management_content}"},
                    {"role": "user", "content": f"Generate a title for a song based on this prompt: {user_message}"}
                ],
                stream=True
            )
            
            title = ""
            for chunk in title_stream:
                if chunk.choices[0].delta.content is not None:
                    title += chunk.choices[0].delta.content
                    self.chat_area.insertPlainText(chunk.choices[0].delta.content)
                    QApplication.processEvents()
            
            self.chat_area.append("\n\nGenerating lyrics...")
            
            # Generate lyrics
            lyrics_stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": lyrics_prompt},
                    {"role": "system", "content": f"Concept:\n{concept_content}"},
                    {"role": "system", "content": f"Composition:\n{composition_content}"},
                    {"role": "system", "content": f"Management:\n{management_content}"},
                    {"role": "user", "content": f"Generate lyrics for a song titled '{title}' based on this prompt: {user_message}"}
                ],
                stream=True
            )
            
            lyrics = ""
            for chunk in lyrics_stream:
                if chunk.choices[0].delta.content is not None:
                    lyrics += chunk.choices[0].delta.content
                    self.chat_area.insertPlainText(chunk.choices[0].delta.content)
                    QApplication.processEvents()
            
            self.update_lyrics(f"Title: {title}\n\n{lyrics}")
        except Exception as e:
            self.chat_area.append(f"Error sending message: {str(e)}")
            self.chat_area.append("Please check your internet connection and the validity of your API key.")

    def update_lyrics(self, new_content):
        self.result_area.setPlainText(new_content)
        self.lyrics_updated.emit(new_content)
        
        # Sauvegarder les paroles dans lyrics.md
        with open('lyrics.md', 'w', encoding='utf-8') as f:
            f.write(new_content)
