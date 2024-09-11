from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from openai import OpenAI
from pydantic import BaseModel
import os
import json
import random
import asyncio

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
        self.fans = self.load_fan_count()  # Load initial number of fans
        self.initUI()
        self.load_api_key()
        self.update_speed = 1000  # Initial update speed in milliseconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_fan_display)
        self.load_system_prompt()
        self.loop = asyncio.get_event_loop()

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

        # Left side - Chat area
        left_layout = QVBoxLayout()
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        left_layout.addWidget(self.result_area)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        left_layout.addWidget(self.chat_area)

        self.start_concert_button = QPushButton("Start Concert")
        self.start_concert_button.clicked.connect(self.evaluate_concert)
        left_layout.addWidget(self.start_concert_button)

        layout.addLayout(left_layout, 1)  # Set stretch factor to 1

        # Right side - Fan count
        right_layout = QVBoxLayout()
        self.fans_label = QLabel(str(self.fans))
        self.fans_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(400)  # Increase the font size to make it extremely large
        self.fans_label.setFont(font)
        self.fans_label.setMinimumSize(800, 600)  # Increase the minimum size to accommodate larger text
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
            self.result_area.append("Concert is taking place...")
            
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a music critic and fan engagement analyst."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            result = json.loads(completion.choices[0].message.content)
            
            # Store the result for later use, but don't display it yet
            self.concert_result = result

            self.update_fans(result['overall_rating'])

            # Call the second GPT for concert feedback
            feedback = self.get_concert_feedback(concept, lyrics, composition)
            self.chat_area.clear()
            self.chat_area.append("Concert Feedback:")
            self.chat_area.append(feedback)

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

        # Clear previous content and display concert results
        self.result_area.clear()
        self.result_area.append(f"Concept Rating: {self.concert_result['concept_rating']}/10")
        self.result_area.append(f"Explanation: {self.concert_result['concept_explanation']}\n")
        
        self.result_area.append(f"Lyrics Rating: {self.concert_result['lyrics_rating']}/10")
        self.result_area.append(f"Explanation: {self.concert_result['lyrics_explanation']}\n")
        
        self.result_area.append(f"Composition Rating: {self.concert_result['composition_rating']}/10")
        self.result_area.append(f"Explanation: {self.concert_result['composition_explanation']}\n")
        
        self.result_area.append(f"Visual Design Rating: {self.concert_result['visual_design_rating']}/10")
        self.result_area.append(f"Explanation: {self.concert_result['visual_design_explanation']}\n")
        
        self.result_area.append(f"Overall Rating: {self.concert_result['overall_rating']}/10")
        self.result_area.append(f"Explanation: {self.concert_result['overall_explanation']}")

        # Update the result area with fan change information
        self.result_area.append(f"\n\nFan count change: {change:+d}\nNew fan count: {self.target_fans}")

    def update_fan_display(self):
        if self.fans != self.target_fans:
            # Add random fluctuation
            fluctuation = random.randint(-5, 5)
            if self.fans < self.target_fans:
                self.fans = min(self.target_fans, max(1, self.fans + 1 + fluctuation))
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
        try:
            with open('band.json', 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        
        data['fans'] = self.fans
        
        with open('band.json', 'w') as f:
            json.dump(data, f)

    def load_system_prompt(self):
        try:
            with open('prompts/concert.md', 'r', encoding='utf-8') as f:
                self.concert_system_prompt = f.read()
        except FileNotFoundError:
            self.concert_system_prompt = "You are an AI assistant providing feedback on concerts."
            print("Warning: prompts/concert.md not found. Using default prompt.")

    def get_concert_feedback(self, concept, lyrics, composition):
        prompt = f"""Provide feedback on the following concert:

Concept:
{concept}

Lyrics:
{lyrics}

Composition:
{composition}

Give detailed feedback on the performance, audience reaction, and overall concert experience."""

        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.concert_system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            
            feedback = completion.choices[0].message.content
            return feedback

        except Exception as e:
            return f"Error getting concert feedback: {str(e)}"
