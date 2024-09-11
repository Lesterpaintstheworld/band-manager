from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLineEdit, QApplication, QMessageBox, QSplitter
from PyQt5.QtCore import pyqtSignal, Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
import time
from openai import OpenAI
import os
from dotenv import load_dotenv
from main import resource_path
from udio_wrapper import UdioWrapper
from pydantic import BaseModel
from typing import List

class ProductionTab(QWidget):
    production_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_api_key()
        self.load_system_prompt()
        self.load_udio_token()

    def initUI(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Partie gauche
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        left_layout.addWidget(self.chat_area)

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)

        left_layout.addLayout(input_layout)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        left_layout.addWidget(self.result_area)

        # Partie droite
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        self.player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)
        right_layout.addWidget(self.video_widget)

        # Splitter pour diviser l'écran
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([int(self.width() * 0.5), int(self.width() * 0.5)])

        main_layout.addWidget(splitter)


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

    def load_udio_token(self):
        load_dotenv()
        self.udio_token = os.getenv('UDIO_AUTH_TOKEN')
        if not self.udio_token:
            print("Error: Udio auth token not found in .env file. Please add UDIO_AUTH_TOKEN to your .env file.")
            self.udio_wrapper = None
        else:
            try:
                self.udio_wrapper = UdioWrapper(self.udio_token)
            except Exception as e:
                print(f"Error initializing Udio wrapper: {str(e)}")
                print("Please check your Udio auth token in the .env file")
                self.udio_wrapper = None

    def load_system_prompt(self):
        try:
            production_prompt = self.read_file(resource_path('prompts/production.md'))
            concept_content = self.read_file(resource_path('concept.md'))
            lyrics_content = self.read_file(resource_path('lyrics.md'))
            composition_content = self.read_file(resource_path('composition.md'))
            visual_design_content = self.read_file(resource_path('visual_design.md'))
            
            self.system_prompt = f"{production_prompt}\n\nContext from concept.md:\n{concept_content}\n\nContext from lyrics.md:\n{lyrics_content}\n\nContext from composition.md:\n{composition_content}\n\nContext from visual_design.md:\n{visual_design_content}"
        except Exception as e:
            self.system_prompt = "You are a creative assistant to help with music production."
            self.chat_area.append(f"Warning: Error loading prompts: {str(e)}. Using a default prompt.")

    def read_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"File {filepath} not found."

    class SongResponse(BaseModel):
        short_prompt: str
        extend_prompts: List[str]
        outro_prompt: str
        num_extensions: int
        custom_lyrics_short: str
        custom_lyrics_extend: List[str]
        custom_lyrics_outro: str

    def send_message(self):
        # Update the system prompt with the latest content
        self.load_system_prompt()
        
        user_message = self.input_field.text()
        self.chat_area.append(f"You: {user_message}")
        self.input_field.clear()

        if not self.api_key or self.client is None:
            self.chat_area.append("Error: OpenAI client not initialized. Please check your API key.")
            return

        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"}
            )
            
            gpt_response = completion.choices[0].message.content
            self.chat_area.append("Assistant: " + gpt_response)
            
            # Parse the JSON response
            import json
            parsed_response = json.loads(gpt_response)
            
            self.update_production(gpt_response)
            self.generate_song(parsed_response)
            
        except Exception as e:
            self.chat_area.append(f"Error sending message: {str(e)}")

    def update_production(self, new_content):
        current_content = self.result_area.toPlainText()
        updated_content = current_content + "\n\n" + new_content
        self.result_area.setPlainText(updated_content)
        self.production_updated.emit(updated_content)

    def generate_song(self, gpt_response):
        if not self.udio_wrapper:
            QMessageBox.critical(self, "Erreur", "Le token d'authentification Udio n'est pas configuré correctement.")
            return

        try:
            self.result_area.clear()
            self.result_area.append("Génération de la chanson en cours...")

            def update_progress(progress):
                self.result_area.append(f"Progression : {progress}%")
                QApplication.processEvents()  # Permet de mettre à jour l'interface utilisateur

            complete_song_sequence = b""
            for chunk in self.udio_wrapper.create_complete_song_stream(**gpt_response):
                complete_song_sequence += chunk
                progress = len(complete_song_sequence) / 1024  # Exemple de calcul de progression
                update_progress(min(int(progress), 100))

            # Sauvegarder le fichier audio dans le dossier songs/
            import os
            song_filename = f"song_{int(time.time())}.mp3"
            song_path = os.path.join("songs", song_filename)
            os.makedirs("songs", exist_ok=True)
            with open(song_path, "wb") as f:
                f.write(complete_song_sequence)
            
            self.result_area.clear()
            self.result_area.setPlainText(f"Chanson générée et sauvegardée : {song_path}")
            
            # Jouer la chanson dans le lecteur audio
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(song_path)))
            self.player.play()
            
            QMessageBox.information(self, "Succès", "La chanson a été générée avec succès.")
            
            # Emit the production_updated signal with the new content
            self.production_updated.emit(complete_song_sequence)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur s'est produite lors de la génération de la chanson : {str(e)}")
