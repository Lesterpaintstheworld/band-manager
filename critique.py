from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from dotenv import load_dotenv
import os
import sys
sys.path.append('.')
from openai import OpenAI
import json

class CritiqueTab(QWidget):
    critique_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_api_key()
        self.load_system_prompt()
        self.client = None

    def initUI(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Chat area
        chat_layout = QVBoxLayout()
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.textChanged.connect(lambda: self.chat_area.ensureCursorVisible())
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

        # Critique display area
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.result_area.textChanged.connect(lambda: self.result_area.ensureCursorVisible())
        layout.addWidget(self.result_area)

    def load_api_key(self):
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            self.chat_area.append("Error: OpenAI API key not found in .env file. Please add OPENAI_API_KEY to your .env file.")
            self.client = None
        else:
            masked_key = f"{self.api_key[:5]}...{self.api_key[-5:]}"
            self.chat_area.append(f"API key found: {masked_key}")
            try:
                self.client = OpenAI(api_key=self.api_key)
                # Removed the models.list() call as it's not necessary and might cause issues
                self.chat_area.append("OpenAI client initialized successfully.")
            except Exception as e:
                self.chat_area.append(f"Error initializing OpenAI client: {str(e)}")
                self.chat_area.append("Please check your API key in the .env file")
                self.client = None

    def load_system_prompt(self):
        try:
            with open('prompts/critique.md', 'r', encoding='utf-8') as f:
                self.system_prompt = f.read()
        except FileNotFoundError:
            self.system_prompt = "You are a music critic providing feedback on songs."
            self.chat_area.append("Warning: prompts/critique.md not found. Using default prompt.")

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
            self.chat_area.append("Assistant: Generating critique...")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"}
            )
            
            critique_json = json.loads(response.choices[0].message.content)
            self.update_critique(critique_json)
        except Exception as e:
            self.chat_area.append(f"Error generating critique: {str(e)}")

    def update_critique(self, critique_json):
        formatted_critique = self.format_critique(critique_json)
        self.result_area.setPlainText(formatted_critique)
        self.critique_updated.emit(formatted_critique)

    def format_critique(self, critique):
        formatted = "Critique:\n\n"
        for aspect in ['concept', 'lyrics', 'composition', 'visual_design']:
            formatted += f"{aspect.capitalize()}:\n"
            formatted += f"Rating: {critique[f'{aspect}_rating']}/10\n"
            formatted += f"Explanation: {critique[f'{aspect}_explanation']}\n\n"
        
        formatted += "Overall:\n"
        formatted += f"Rating: {critique['overall_rating']}/10\n"
        formatted += f"Explanation: {critique['overall_explanation']}\n"
        
        return formatted
