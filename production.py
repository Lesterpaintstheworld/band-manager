from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTextEdit, QLabel
from PyQt5.QtCore import Qt

class ProductionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area, 1)

        self.result_area = QLabel("Production result will be displayed here")
        self.result_area.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_area, 1)

        # TODO: Implement chat functionality with GPT-4-mini
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from dotenv import load_dotenv
import os
import sys
sys.path.append('.')
from openai import OpenAI

class ProductionTab(QWidget):
    production_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_api_key()
        self.load_system_prompt()
        self.client = None
        self.load_initial_production()

    def load_initial_production(self):
        try:
            with open('production.md', 'r', encoding='utf-8') as f:
                initial_production = f.read()
            self.result_area.setPlainText(initial_production)
        except FileNotFoundError:
            self.chat_area.append("Warning: production.md file not found. Starting with empty production notes.")

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

        # Production display area
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
            except Exception as e:
                print(f"Error initializing OpenAI client: {str(e)}")
                print("Please check your API key in the .env file")
                self.client = None

    def load_system_prompt(self):
        try:
            with open('prompts/production.md', 'r', encoding='utf-8') as f:
                production_prompt = f.read()
            
            with open('concept.md', 'r', encoding='utf-8') as f:
                concept_content = f.read()
            
            with open('lyrics.md', 'r', encoding='utf-8') as f:
                lyrics_content = f.read()
            
            with open('composition.md', 'r', encoding='utf-8') as f:
                composition_content = f.read()
            
            self.system_prompt = f"{production_prompt}\n\nContext from concept.md:\n{concept_content}\n\nContext from lyrics.md:\n{lyrics_content}\n\nContext from composition.md:\n{composition_content}"
        except FileNotFoundError as e:
            self.system_prompt = "You are a creative assistant to help with music production."
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
            self.chat_area.append("Assistant: ")
            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                stream=True
            )
            
            production_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    production_response += content
                    self.chat_area.insertPlainText(content)
                    QApplication.processEvents()
            
            self.update_production(production_response)
        except Exception as e:
            self.chat_area.append(f"Error generating production notes: {str(e)}")

    def update_production(self, new_content):
        current_production = self.result_area.toPlainText()
        updated_production = current_production + "\n\n" + new_content
        self.result_area.setPlainText(updated_production)
        self.production_updated.emit(updated_production)
        
        # Sauvegarder les notes de production dans production.md
        with open('production.md', 'w', encoding='utf-8') as f:
            f.write(updated_production)
