from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from openai import OpenAI
import os
import json

class ConcertTab(QWidget):
    def __init__(self):
        super().__init__()
        self.fans = 1000  # Initial number of fans
        self.initUI()
        self.load_api_key()
        self.update_speed = 100  # Initial update speed in milliseconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_fan_display)

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)

        self.fans_label = QLabel(str(self.fans))
        self.fans_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(48)  # Make the font size very large
        self.fans_label.setFont(font)
        layout.addWidget(self.fans_label)

        self.start_concert_button = QPushButton("Start Concert")
        self.start_concert_button.clicked.connect(self.evaluate_concert)
        layout.addWidget(self.start_concert_button)

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
        prompt = f"""Evaluate the following aspects of a song and give a rating out of 10 for each:

Concept:
{concept}

Lyrics:
{lyrics}

Composition:
{composition}

Visual Design:
{visual_design}

For each aspect, provide a brief explanation for the rating. Then, give an overall rating out of 10 for the entire song.
Finally, based on the overall rating, calculate the change in fan count. Use these rules:
- If the overall rating is less than 5, decrease fans by 10%
- If the overall rating is between 5 and 7, increase fans by 5%
- If the overall rating is above 7, increase fans by 20%

Present the results in a clear, formatted manner."""

        try:
            self.result_area.clear()
            self.result_area.append("Evaluating concert...")
            
            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a music critic and fan engagement analyst."},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )
            
            result = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    result += content
                    self.result_area.insertPlainText(content)
                    self.result_area.ensureCursorVisible()

            # Extract overall rating and update fan count
            overall_rating = float(result.split("Overall Rating:")[-1].split("/10")[0].strip())
            self.update_fans(overall_rating)

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
        self.update_speed = 100  # Reset update speed
        self.timer.start(self.update_speed)

        # Update the result area with fan change information
        current_text = self.result_area.toPlainText()
        self.result_area.append(f"\n\nFan count change: {change:+d}\nNew fan count: {self.target_fans}")

    def update_fan_display(self):
        if self.fans != self.target_fans:
            step = max(1, abs(self.fan_change) // 100)  # Adjust step size based on total change
            if self.fans < self.target_fans:
                self.fans = min(self.fans + step, self.target_fans)
            else:
                self.fans = max(self.fans - step, self.target_fans)
            
            self.fans_label.setText(str(self.fans))
            
            # Gradually increase update speed
            self.update_speed = max(10, self.update_speed - 1)
            self.timer.setInterval(self.update_speed)
        else:
            self.timer.stop()
            self.save_fan_count()

    def save_fan_count(self):
        data = {'fans': self.fans}
        with open('band.json', 'w') as f:
            json.dump(data, f)
