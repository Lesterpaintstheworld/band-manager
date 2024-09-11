from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLabel, QPushButton, QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from openai import OpenAI
import os
import sys
import json
import random
import math

class ConcertTab(QWidget):
    def __init__(self):
        super().__init__()
        self.fans = self.load_fan_count()
        self.initUI()
        self.client = None
        self.load_api_key()
        self.update_speed = 1000
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_fan_display)
        self.load_system_prompt()

    def load_fan_count(self):
        try:
            with open('band.json', 'r') as f:
                data = json.load(f)
                return max(1, data.get('fans', 1))
        except (FileNotFoundError, json.JSONDecodeError):
            return 1

    def initUI(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        left_layout = QVBoxLayout()
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        left_layout.addWidget(self.chat_area)

        self.start_concert_button = QPushButton("Start Concert")
        self.start_concert_button.clicked.connect(self.start_concert)
        left_layout.addWidget(self.start_concert_button)

        layout.addLayout(left_layout, 1)

        right_layout = QVBoxLayout()
        self.fans_label = QLabel(str(self.fans))
        self.fans_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(400)
        self.fans_label.setFont(font)
        self.fans_label.setMinimumSize(800, 600)
        right_layout.addWidget(self.fans_label)

        layout.addLayout(right_layout, 1)

    def load_api_key(self):
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY='):
                        api_key = line.split('=')[1].strip()
                        self.client = OpenAI(api_key=api_key)
                        return
                self.chat_area.append("Error: OpenAI API key not found in .env file.")
        except FileNotFoundError:
            self.chat_area.append("Error: .env file not found. Please make sure it exists and contains your OpenAI API key.")
        self.client = None

    def start_concert(self):
        audience_size = math.ceil(self.fans * 1.2)

        prompt = f"""Create a short, engaging story about the band's concert performance of their new song. Use the following information:

Concept:
{self.concept_prompt}

Lyrics:
{self.lyrics_prompt}

Composition:
{self.composition_prompt}

Visual Design:
{self.visual_design_prompt}

Critique:
{self.critique_prompt}

Audience Size: {audience_size}

{self.concert_system_prompt}"""

        try:
            self.chat_area.clear()
            self.chat_area.append("Generating concert story...")
            
            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a creative writer narrating concert experiences."},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )
            
            self.chat_area.clear()
            concert_story = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    concert_story += content
                    self.chat_area.insertPlainText(content)
                    QApplication.processEvents()

            self.update_fans(audience_size)

        except Exception as e:
            self.chat_area.append(f"Error during concert: {str(e)}")

    def read_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"File {filename} not found."

    def update_fans(self, audience_size):
        change = random.randint(-int(audience_size * 0.1), int(audience_size * 0.2))
        self.target_fans = max(1, self.fans + change)
        self.fan_change = change
        self.update_speed = 1000
        self.update_acceleration = 0.95
        self.timer.start(self.update_speed)

        self.chat_area.append(f"\n\nFan count change: {change:+d}\nNew fan count: {self.target_fans}")

    def update_fan_display(self):
        if self.fans != self.target_fans:
            fluctuation = random.randint(-5, 5)
            if self.fans < self.target_fans:
                self.fans = min(self.target_fans, self.fans + 1 + fluctuation)
            else:
                self.fans = max(self.target_fans, self.fans - 1 + fluctuation)
            
            self.fans_label.setText(f"{self.fans:,}")
            
            self.update_speed = max(10, int(self.update_speed * self.update_acceleration))
            self.timer.setInterval(self.update_speed)
        else:
            self.timer.stop()
            self.save_fan_count()

    def save_fan_count(self):
        try:
            with open('band.json', 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        
        data['fans'] = self.fans
        
        with open('band.json', 'w') as f:
            json.dump(data, f)

    def get_resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def load_system_prompt(self):
        file_name = 'prompts/concert.md'
        full_path = self.get_resource_path(file_name)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                self.concert_system_prompt = f.read()
        except FileNotFoundError:
            error_message = f"Erreur : Le fichier {full_path} n'a pas été trouvé. Veuillez vérifier que le fichier de prompt prompts/concert.md est présent."
            print(error_message)
            QMessageBox.critical(self, "Erreur de chargement", error_message)
            sys.exit(1)
