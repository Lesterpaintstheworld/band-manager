from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLineEdit, QApplication, QMessageBox, QSplitter
from PyQt5.QtCore import pyqtSignal, Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
import time
import logging
from openai import OpenAI
import os
from dotenv import load_dotenv
from main import resource_path
import requests
from pydantic import BaseModel
from typing import List
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionTab(QWidget):
    production_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_api_key()
        self.load_system_prompt()

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
        if not user_message:
            self.chat_area.append("Error: Empty input. Please enter a prompt.")
            return

        self.chat_area.append(f"You: {user_message}")
        self.input_field.clear()

        if not self.api_key or self.client is None:
            self.chat_area.append("Error: OpenAI client not initialized. Please check your API key.")
            return

        try:
            stream = self.client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Generate a JSON response for the following request: {user_message}"}
                ],
                response_format={"type": "json_object"},
                stream=True
            )
            
            gpt_response = ""
            self.chat_area.append("Assistant: ")
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    gpt_response += chunk.choices[0].delta.content
                    self.chat_area.append(chunk.choices[0].delta.content)
                    QApplication.processEvents()  # Update the UI
            
            # Parse the JSON response
            import json
            parsed_response = json.loads(gpt_response)
            
            self.update_production(gpt_response)
            self.display_song_info(parsed_response)
            
        except Exception as e:
            self.chat_area.append(f"Error sending message: {str(e)}")

    def update_production(self, new_content):
        current_content = self.result_area.toPlainText()
        updated_content = current_content + "\n\n" + new_content
        self.result_area.setPlainText(updated_content)
        self.production_updated.emit(updated_content)

    def display_song_info(self, song_info):
        self.result_area.clear()
        self.result_area.append("Song Information (Conceptual Only):")
        self.result_area.append("Note: This is a conceptual representation. No audio is generated.")
        self.result_area.append(f"Short Prompt: {song_info['short_prompt']}")
        self.result_area.append(f"Number of Extensions: {song_info['num_extensions']}")
        self.result_area.append(f"Outro Prompt: {song_info['outro_prompt']}")
        self.result_area.append("\nExtend Prompts:")
        for i, prompt in enumerate(song_info['extend_prompts'], 1):
            self.result_area.append(f"{i}. {prompt}")
        self.result_area.append("\nCustom Lyrics:")
        self.result_area.append(f"Short: {song_info['custom_lyrics_short']}")
        self.result_area.append("Extended:")
        for i, lyric in enumerate(song_info['custom_lyrics_extend'], 1):
            self.result_area.append(f"{i}. {lyric}")
        self.result_area.append(f"Outro: {song_info['custom_lyrics_outro']}")
        self.result_area.append("\nReminder: This is a conceptual representation only. No actual audio is generated or played.")

    def handle_player_error(self, error):
        error_msg = f"Media player error: {error}"
        if error == QMediaPlayer.FormatError:
            error_msg += " (Format Error: The media format is not supported.)"
        elif error == QMediaPlayer.NetworkError:
            error_msg += " (Network Error: A network error occurred.)"
        elif error == QMediaPlayer.AccessDeniedError:
            error_msg += " (Access Denied Error: There was a permissions issue.)"
        elif error == QMediaPlayer.ServiceMissingError:
            error_msg += " (Service Missing Error: A required media service is missing.)"
        elif error == QMediaPlayer.ResourceError:
            error_msg += " (Resource Error: The media resource could not be resolved.)"
        else:
            error_msg += f" (Error code: {error})"
        
        self.chat_area.append(error_msg)
        logger.error(error_msg)

        # Try to get more information about the media
        media_status = self.player.mediaStatus()
        self.chat_area.append(f"Media status: {media_status}")
        logger.info(f"Media status: {media_status}")

        # Check supported audio formats
        supported_formats = QMediaPlayer.supportedMimeTypes()
        self.chat_area.append(f"Supported audio formats: {', '.join(supported_formats)}")
        logger.info(f"Supported audio formats: {', '.join(supported_formats)}")

    def handle_user_prompt(self):
        user_prompt = self.input_field.text()
        if user_prompt:
            self.chat_area.append(f"You: {user_prompt}")
            self.input_field.clear()
            self.send_message()
        # Removed the else clause to prevent the warning when there's input
