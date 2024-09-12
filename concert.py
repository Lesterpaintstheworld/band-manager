from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLabel, QPushButton, QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from openai import OpenAI
import os
import sys
import json
import random
import math
import logging
from main import resource_path

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
        self.load_other_prompts()

    def load_fan_count(self):
        try:
            with open(resource_path('band.json'), 'r') as f:
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
        self.chat_area.append("Hello! I'm Spark, your concert coordinator. Welcome to the Concert Tab! Here you can simulate your band's concert performance. Click the 'Start Concert' button when you're ready to perform and see how your fan base grows!")
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
            with open(resource_path('.env'), 'r') as f:
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

        # Charger les contenus les plus récents
        management_content = self.read_file(resource_path('management.md'))
        concept_content = self.read_file(resource_path('concept.md'))
        lyrics_content = self.read_file(resource_path('lyrics.md'))
        composition_content = self.read_file(resource_path('composition.md'))
        production_content = self.read_file(resource_path('production.md'))
        visual_design_content = self.read_file(resource_path('visual_design.md'))
        critique_content = self.read_file(resource_path('critique.md'))

        prompt = f"""Create a short, engaging story about the band's concert performance of their new song. Use the provided information.

Audience Size: {audience_size}
Current Fan Count: {self.fans}

{self.concert_system_prompt}"""

        try:
            self.chat_area.clear()
            self.chat_area.append("Generating concert story...")
            
            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "system", "content": f"Management:\n{management_content}"},
                    {"role": "system", "content": f"Concept:\n{concept_content}"},
                    {"role": "system", "content": f"Lyrics:\n{lyrics_content}"},
                    {"role": "system", "content": f"Composition:\n{composition_content}"},
                    {"role": "system", "content": f"Visual Design:\n{visual_design_content}"},
                    {"role": "system", "content": f"Production:\n{production_content}"},
                    {"role": "system", "content": f"Critique:\n{critique_content}"},
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
            error_message = f"Erreur lors du concert : {str(e)}"
            self.chat_area.append(error_message)
            logging.error(error_message)

    def read_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"File {filename} not found."

    def update_fans(self, audience_size):
        # Calculate a base increase
        base_increase = int(audience_size * 0.1)
        
        # Add a random factor
        random_factor = random.randint(0, base_increase)
        
        # Calculate total change
        change = base_increase + random_factor
        
        self.target_fans = max(1, self.fans + change)
        self.fan_change = change
        self.update_speed = 1000
        self.update_acceleration = 0.95
        self.timer.start(self.update_speed)

        self.chat_area.append(f"\n\nFan count change: +{change:,}\nNew fan count: {self.target_fans:,}")

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
            with open(resource_path('band.json'), 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        
        data['fans'] = self.fans
        
        with open(resource_path('band.json'), 'w') as f:
            json.dump(data, f)

    def load_system_prompt(self):
        file_name = 'prompts/concert.md'
        full_path = resource_path(file_name)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                self.concert_system_prompt = f.read()
        except FileNotFoundError:
            error_message = f"Erreur : Le fichier {full_path} n'a pas été trouvé. Veuillez vérifier que le fichier de prompt prompts/concert.md est présent."
            print(error_message)
            QMessageBox.critical(self, "Erreur de chargement", error_message)
            sys.exit(1)

    def load_system_prompt(self):
        try:
            with open(resource_path('prompts/concert.md'), 'r', encoding='utf-8') as f:
                self.system_prompt = f.read()
        except FileNotFoundError:
            error_message = f"Erreur : Le fichier prompts/concert.md n'a pas été trouvé."
            print(error_message)
            self.system_prompt = "You are an AI assistant helping with concert simulations."

    def load_other_prompts(self):
        prompt_files = ['concept.md', 'lyrics.md', 'composition.md', 'visual_design.md', 'critique.md']
        for file in prompt_files:
            attr_name = file.split('.')[0] + '_prompt'
            full_path = resource_path(os.path.join('prompts', file))
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    setattr(self, attr_name, f.read())
            except FileNotFoundError:
                error_message = f"Erreur : Le fichier {full_path} n'a pas été trouvé."
                print(error_message)
                setattr(self, attr_name, "")
