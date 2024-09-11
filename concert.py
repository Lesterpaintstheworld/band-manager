from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from openai import OpenAI
from pydantic import BaseModel
import os
import json
import random

class EvaluationResult(BaseModel):
    concept_rating: int
    lyrics_rating: int
    composition_rating: int
    visual_design_rating: int
    overall_rating: int
    concept_explanation: str
    lyrics_explanation: str
    composition_explanation: str
    visual_design_explanation: str
    overall_explanation: str

class ConcertTab(QWidget):
    def __init__(self):
        super().__init__()
        self.fans = 1000  # Initial number of fans
        self.initUI()
        self.load_api_key()
        self.update_speed = 1000  # Initial update speed in milliseconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_fan_display)

    def initUI(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Left side - Chat area
        left_layout = QVBoxLayout()
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        left_layout.addWidget(self.result_area)

        self.start_concert_button = QPushButton("Start Concert")
        self.start_concert_button.clicked.connect(self.evaluate_concert)
        left_layout.addWidget(self.start_concert_button)

        layout.addLayout(left_layout, 1)  # Set stretch factor to 1

        # Right side - Fan count
        right_layout = QVBoxLayout()
        self.fans_label = QLabel(str(self.fans))
        self.fans_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(144)  # Make the font size very large
        self.fans_label.setFont(font)
        right_layout.addWidget(self.fans_label)

        layout.addLayout(right_layout, 1)  # Set stretch factor to 1

    def load_api_key(self):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    api_key = line.split('=')[1].strip()
                    self.client = OpenAI(api_key=api_key)
                    break
            else:
                self.result_area.append("Error: OpenAI API key not found in .env file.")

    def evaluate_concert(self):
        # Read content from all relevant files
        concept = self.read_file('concept.md')
        lyrics = self.read_file('lyrics.md')
        composition = self.read_file('composition.md')
        visual_design = self.read_file('visual_design.md')

        # Prepare the prompt for GPT
        prompt = f"""Evaluate the following aspects of a song:

Concept:
{concept}

Lyrics:
{lyrics}

Composition:
{composition}

Visual Design:
{visual_design}

Provide a rating out of 10 and a brief explanation for each aspect. Then, give an overall rating out of 10 for the entire song with an explanation. Format your response as a JSON object with the following structure:
{{
    "concept_rating": int,
    "concept_explanation": "string",
    "lyrics_rating": int,
    "lyrics_explanation": "string",
    "composition_rating": int,
    "composition_explanation": "string",
    "visual_design_rating": int,
    "visual_design_explanation": "string",
    "overall_rating": int,
    "overall_explanation": "string"
}}"""

        try:
            self.result_area.clear()
            self.result_area.append("Evaluating concert...")
            
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a music critic and fan engagement analyst."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            result = json.loads(completion.choices[0].message.content)
            
            self.result_area.append(f"Concept Rating: {result['concept_rating']}/10")
            self.result_area.append(f"Explanation: {result['concept_explanation']}\n")
            
            self.result_area.append(f"Lyrics Rating: {result['lyrics_rating']}/10")
            self.result_area.append(f"Explanation: {result['lyrics_explanation']}\n")
            
            self.result_area.append(f"Composition Rating: {result['composition_rating']}/10")
            self.result_area.append(f"Explanation: {result['composition_explanation']}\n")
            
            self.result_area.append(f"Visual Design Rating: {result['visual_design_rating']}/10")
            self.result_area.append(f"Explanation: {result['visual_design_explanation']}\n")
            
            self.result_area.append(f"Overall Rating: {result['overall_rating']}/10")
            self.result_area.append(f"Explanation: {result['overall_explanation']}")

            self.update_fans(result['overall_rating'])

        except Exception as e:
            self.result_area.append(f"Error during evaluation: {str(e)}")

    def read_file(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"File {filename} not found."

    def update_fans(self, overall_rating):
        if overall_rating < 5:
            change = int(-self.fans * 0.1)
        elif 5 <= overall_rating < 7:
            change = int(self.fans * 0.05)
        else:
            change = int(self.fans * 0.2)

        self.target_fans = max(0, self.fans + change)  # Ensure fan count doesn't go negative
        self.fan_change = change
        self.update_speed = 1000  # Start with a slow update speed
        self.update_acceleration = 0.95  # Factor to accelerate updates
        self.timer.start(self.update_speed)

        # Update the result area with fan change information
        current_text = self.result_area.toPlainText()
        self.result_area.append(f"\n\nFan count change: {change:+d}\nNew fan count: {self.target_fans}")

    def update_fan_display(self):
        if self.fans != self.target_fans:
            # Add random fluctuation
            fluctuation = random.randint(-5, 5)
            if self.fans < self.target_fans:
                self.fans = min(self.target_fans, self.fans + 1 + fluctuation)
            else:
                self.fans = max(self.target_fans, self.fans - 1 + fluctuation)
            
            self.fans_label.setText(f"{self.fans:,}")  # Format with commas for readability
            
            # Gradually increase update speed
            self.update_speed = max(10, int(self.update_speed * self.update_acceleration))
            self.timer.setInterval(self.update_speed)
        else:
            self.timer.stop()
            self.save_fan_count()

    def save_fan_count(self):
        data = {'fans': self.fans}
        with open('band.json', 'w') as f:
            json.dump(data, f)
