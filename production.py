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
from udio_wrapper import UdioAuthenticator, UdioSongGenerator, UdioWrapper
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
        self.udio_token1 = os.getenv('UDIO_AUTH_TOKEN1')
        self.udio_token2 = os.getenv('UDIO_AUTH_TOKEN2')
        if not self.udio_token1 or not self.udio_token2:
            self.chat_area.append("Error: Udio authentication tokens not found in .env file.")
            self.chat_area.append("Please add UDIO_AUTH_TOKEN1 and UDIO_AUTH_TOKEN2 to your .env file.")
            self.udio_wrapper = None
        else:
            try:
                from udio_wrapper import UdioAuthenticator, UdioWrapper
                authenticator = UdioAuthenticator(self.udio_token1, self.udio_token2)
                self.udio_wrapper = UdioWrapper(authenticator)
                self.chat_area.append("Udio connection initialized successfully.")
            except Exception as e:
                self.chat_area.append(f"Error initializing Udio connection: {str(e)}")
                self.chat_area.append("Please check your Udio authentication tokens in the .env file.")
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
            stream = self.client.chat.completions.create(
                model="gpt-4o-mini",
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
            error_message = "Error: The Udio connection is not configured correctly or the connection to Udio failed."
            self.chat_area.append(error_message)
            QMessageBox.critical(self, "Error", error_message)
            return

        try:
            self.result_area.clear()
            self.result_area.append("Generating song...")
            self.chat_area.append("Starting song generation...")

            song_data = self.udio_wrapper.create_complete_song(
                short_prompt=gpt_response['short_prompt'],
                extend_prompts=gpt_response['extend_prompts'],
                outro_prompt=gpt_response['outro_prompt'],
                num_extensions=gpt_response['num_extensions'],
                custom_lyrics_short=gpt_response['custom_lyrics_short'],
                custom_lyrics_extend=gpt_response['custom_lyrics_extend'],
                custom_lyrics_outro=gpt_response['custom_lyrics_outro']
            )

            if not song_data:
                raise Exception("The generated song data is empty.")

            # Save the audio file in the songs/ folder
            song_filename = f"song_{int(time.time())}.mp3"
            song_path = os.path.join("songs", song_filename)
            os.makedirs("songs", exist_ok=True)
            
            with open(song_path, 'wb') as f:
                f.write(song_data)
            
            self.result_area.clear()
            self.result_area.append(f"Song generated and saved: {song_path}")
            self.chat_area.append(f"Song generated and saved: {song_path}")
            
            # Play the song in the audio player
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(song_path)))
            self.player.play()
            
            QMessageBox.information(self, "Success", "The song has been generated successfully.")
            
            # Emit the production_updated signal with the new content
            self.production_updated.emit(song_path)
        except Exception as e:
            error_message = f"An error occurred while generating the song: {str(e)}"
            self.chat_area.append(error_message)
            self.result_area.append(f"Error: {str(e)}")
            logger.error(f"Song generation error: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Error", error_message)
