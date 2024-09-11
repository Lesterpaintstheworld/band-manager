from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QPushButton
from PyQt5.QtCore import Qt
import random

class ConcertTab(QWidget):
    def __init__(self):
        super().__init__()
        self.fans = 1000  # Nombre initial de fans
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area)

        self.result_area = QLabel(f"Nombre de fans actuel : {self.fans}")
        self.result_area.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_area)

        self.evaluate_button = QPushButton("Évaluer le concert")
        self.evaluate_button.clicked.connect(self.evaluate_concert)
        layout.addWidget(self.evaluate_button)

    def evaluate_concert(self):
        concept_score = self.evaluate_phase("concept")
        lyrics_score = self.evaluate_phase("paroles")
        music_score = self.evaluate_phase("prompts musicaux")
        image_score = self.evaluate_phase("prompt d'image")

        total_score = (concept_score + lyrics_score + music_score + image_score) / 4

        fans_change = self.calculate_fans_change(total_score)
        self.update_fans(fans_change)

        self.display_results(concept_score, lyrics_score, music_score, image_score, total_score, fans_change)

    def evaluate_phase(self, phase):
        # Simulation d'évaluation (à remplacer par une véritable logique d'évaluation)
        return random.uniform(0, 10)

    def calculate_fans_change(self, score):
        # Calcul du changement de fans basé sur le score
        if score < 5:
            return int(-self.fans * 0.1)  # Perte de 10% des fans
        elif 5 <= score < 7:
            return int(self.fans * 0.05)  # Gain de 5% des fans
        else:
            return int(self.fans * 0.2)  # Gain de 20% des fans

    def update_fans(self, change):
        self.fans += change
        self.fans = max(0, self.fans)  # Assurez-vous que le nombre de fans ne soit pas négatif

    def display_results(self, concept_score, lyrics_score, music_score, image_score, total_score, fans_change):
        result = f"Résultats du concert :\n"
        result += f"Concept : {concept_score:.2f}/10\n"
        result += f"Paroles : {lyrics_score:.2f}/10\n"
        result += f"Musique : {music_score:.2f}/10\n"
        result += f"Image : {image_score:.2f}/10\n"
        result += f"Score total : {total_score:.2f}/10\n"
        result += f"Changement de fans : {fans_change:+d}\n"
        result += f"Nombre de fans actuel : {self.fans}"

        self.chat_area.setText(result)
        self.result_area.setText(f"Nombre de fans actuel : {self.fans}")
