from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QApplication, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
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
        critique_layout = QVBoxLayout()
        self.critic_name_label = QLabel()
        self.critic_name_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.critic_name_label.setFont(font)
        critique_layout.addWidget(self.critic_name_label)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.result_area.textChanged.connect(lambda: self.result_area.ensureCursorVisible())
        critique_layout.addWidget(self.result_area)

        layout.addLayout(critique_layout)

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
            with open('prompts/critique.md', 'r', encoding='utf-8') as f:
                self.system_prompt = f.read()
        except FileNotFoundError:
            self.system_prompt = "You are a music critic providing feedback on songs."
            self.chat_area.append("Warning: prompts/critique.md not found. Using default prompt.")
        
        # Load the current fan count
        try:
            with open('band.json', 'r') as f:
                data = json.load(f)
                self.fan_count = data.get('fans', 1)
        except (FileNotFoundError, json.JSONDecodeError):
            self.fan_count = 1
        
        # Set the critic name
        self.set_critic_name()
        
        # Append fan count and instructions to the system prompt
        self.system_prompt += f"\n\nCurrent fan count: {self.fan_count}\n\n"
        self.system_prompt += "Please provide your critique in a natural, conversational format. Include ratings out of 10 for each aspect (concept, lyrics, composition, visual design, production) and an overall rating. Explain your ratings and provide constructive feedback for each aspect. Conclude with an overall assessment of the song."

    def read_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"File {filepath} not found."

    def set_critic_name(self):
        if self.fan_count <= 10:
            critic_name = "Your Mom"
        elif self.fan_count <= 100:
            critic_name = "Local Music Blogger"
        elif self.fan_count <= 1000:
            critic_name = "College Radio DJ"
        elif self.fan_count <= 10000:
            critic_name = "Music Magazine Reviewer"
        elif self.fan_count <= 100000:
            critic_name = "Respected Music Journalist"
        elif self.fan_count <= 1000000:
            critic_name = "Renowned Music Critic"
        else:
            critic_name = "Worldwide Tastemaker"
        
        self.critic_name_label.setText(critic_name)

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
            if not user_message.strip():
                self.chat_area.append("Assistant: It seems you haven't provided a specific song to critique. Here's how I would approach a song critique:")
                self.chat_area.append("\n1. Listen to the song carefully, multiple times if necessary.")
                self.chat_area.append("2. Analyze the following aspects:")
                self.chat_area.append("   - Concept: The overall theme or idea behind the song")
                self.chat_area.append("   - Lyrics: The quality and meaning of the words")
                self.chat_area.append("   - Composition: The musical structure, melody, and harmony")
                self.chat_area.append("   - Visual Design: If there's a music video or album art")
                self.chat_area.append("3. Rate each aspect out of 10 and provide constructive feedback.")
                self.chat_area.append("4. Give an overall rating and summarize your thoughts.")
                self.chat_area.append("\nWhen you're ready to critique a specific song, please provide its details.")
                return

            self.chat_area.append("Assistant: Generating critique...")
            # Read content from relevant files
            concept_content = self.read_file('concept.md')
            lyrics_content = self.read_file('lyrics.md')
            composition_content = self.read_file('composition.md')
            visual_design_content = self.read_file('visual_design.md')
            production_content = self.read_file('production.md')

            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "system", "content": f"Concept:\n{concept_content}"},
                    {"role": "system", "content": f"Lyrics:\n{lyrics_content}"},
                    {"role": "system", "content": f"Composition:\n{composition_content}"},
                    {"role": "system", "content": f"Visual Design:\n{visual_design_content}"},
                    {"role": "system", "content": f"Production:\n{production_content}"},
                    {"role": "user", "content": f"Generate a critique for the following: {user_message}"}
                ],
                stream=True
            )
            
            critique_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    critique_response += content
                    self.chat_area.insertPlainText(content)
                    QApplication.processEvents()
            
            self.update_critique(critique_response)
        except Exception as e:
            self.chat_area.append(f"Error generating critique: {str(e)}")

    def update_critique(self, critique_text):
        self.result_area.setPlainText(critique_text)
        self.critique_updated.emit(critique_text)
