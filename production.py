from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLineEdit, QApplication, QMessageBox, QSplitter, QSlider, QFrame
from PyQt5.QtCore import pyqtSignal, Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist, QAudio
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QPainter, QColor, QPen
from waveform_widget import WaveformWidget
import time
import logging
from openai import OpenAI
import os
from dotenv import load_dotenv
from main import resource_path
import requests
from pydantic import BaseModel
from typing import List
import json
from PyQt5.QtCore import QThread, pyqtSignal
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
        self.check_udiopro_api_key()
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

    def check_udiopro_api_key(self):
        udiopro_api_key = os.getenv('UDIOPRO_API_KEY')
        if not udiopro_api_key:
            self.result_area.append("Warning: UdioPro API key not found. Please add UDIOPRO_API_KEY to your .env file.")
            logging.warning("UdioPro API key not found in .env file.")

    def initUI(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Left part
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("font-size: 14pt;")
        left_layout.addWidget(self.chat_area)

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setStyleSheet("font-size: 14pt;")
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("font-size: 14pt;")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)

        left_layout.addLayout(input_layout)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.result_area.setStyleSheet("font-size: 14pt;")
        left_layout.addWidget(self.result_area)

        # Right part
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        # Player frame
        player_frame = QFrame()
        player_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        player_layout = QVBoxLayout()
        player_frame.setLayout(player_layout)

        self.player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)
        player_layout.addWidget(self.video_widget)

        # Waveform widget
        self.waveform_widget = WaveformWidget()
        player_layout.addWidget(self.waveform_widget)

        # Audio controls
        controls_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)

        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.pause_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.volume_slider)

        player_layout.addLayout(controls_layout)

        # Center the player frame vertically
        right_layout.addStretch()
        right_layout.addWidget(player_frame)
        right_layout.addStretch()

        # Connect audio control signals
        self.play_button.clicked.connect(self.player.play)
        self.pause_button.clicked.connect(self.player.pause)
        self.stop_button.clicked.connect(self.player.stop)
        self.volume_slider.valueChanged.connect(self.set_volume)

        # Connect player signals for waveform update
        self.player.positionChanged.connect(self.waveform_widget.update_position)
        self.player.durationChanged.connect(self.waveform_widget.set_duration)

        # Splitter to divide the screen
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
            self.chat_area.append("Debug: Displaying song information (no audio generation)")
            logging.info("Displaying song information in production tab (no audio generation)")
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
        self.result_area.append("Debug: Starting to display song information")
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
        self.result_area.append("Debug: Finished displaying song information")
        logging.info("Song information displayed in the production tab")
        
        # Call UdioPro API
        self.call_udiopro_api(song_info)

    def call_udiopro_api(self, song_info):
        self.result_area.append("\nDebug: Calling UdioPro API")
        logging.info("Calling UdioPro API")

        # Construct the prompt for UdioPro
        prompt = f"{song_info['short_prompt']} "
        prompt += " ".join(song_info['extend_prompts'])
        prompt += f" {song_info['outro_prompt']}"

        self.worker = UdioProWorker(prompt, os.getenv('UDIOPRO_API_KEY'))
        self.worker.result_ready.connect(self.display_udiopro_result)
        self.worker.error_occurred.connect(self.handle_udiopro_error)
        self.worker.start()

        self.result_area.append("\nNote: UdioPro API call initiated. Please wait for the result.")
        logging.info("UdioPro API call initiated")

    def handle_udiopro_error(self, error_message):
        self.result_area.append(f"Error: {error_message}")
        logging.error(error_message)

    def fetch_udiopro_result(self, work_id):
        self.result_area.append("\nDebug: Fetching result from UdioPro API")
        logging.info("Fetching result from UdioPro API")

        url = f"https://udioapi.pro/api/feed"
        params = {
            "workId": work_id
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('UDIOPRO_API_KEY')}"
        }

        max_attempts = 30
        attempt = 0

        while attempt < max_attempts:
            try:
                response = requests.get(url, params=params, headers=headers)
                response.raise_for_status()
                result = response.json()

                if result['type'] == 'complete':
                    self.display_udiopro_result(result)
                    break
                elif result['type'] in ['new', 'text', 'first']:
                    self.result_area.append(f"Debug: UdioPro generation in progress. Status: {result['type']}")
                    time.sleep(10)  # Wait for 10 seconds before next attempt
                else:
                    self.result_area.append(f"Debug: Unexpected result type: {result['type']}")
                    break

            except requests.RequestException as e:
                self.result_area.append(f"Error fetching UdioPro result: {str(e)}")
                logging.error(f"Error fetching UdioPro result: {str(e)}")
                break

            attempt += 1

        if attempt == max_attempts:
            self.result_area.append("Error: Maximum attempts reached while fetching UdioPro result")
            logging.error("Maximum attempts reached while fetching UdioPro result")

    def download_and_play_audio(self, audio_url, song_title):
        try:
            response = requests.get(audio_url)
            response.raise_for_status()

            # Create a 'generated_songs' directory if it doesn't exist
            os.makedirs('generated_songs', exist_ok=True)

            # Generate a filename based on the song title
            filename = os.path.join('generated_songs', f"{song_title.replace(' ', '_')}_{int(time.time())}.mp3")

            # Save the audio file
            with open(filename, 'wb') as f:
                f.write(response.content)

            # Add the audio to the playlist
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(filename)))

            # If this is the first song, start playing
            if self.playlist.mediaCount() == 1:
                self.player.setPlaylist(self.playlist)
                self.player.play()

            self.result_area.append(f"Audio saved and added to playlist: {filename}")
            logging.info(f"Audio saved and added to playlist: {filename}")
            
            # Open the folder containing the saved file
            os.startfile(os.path.dirname(filename))
        except Exception as e:
            self.result_area.append(f"Error downloading audio: {str(e)}")
            logging.error(f"Error downloading audio: {str(e)}")

    def display_udiopro_result(self, result):
        self.result_area.append("\nUdioPro Generation Result:")
        self.result_area.append(f"Type: {result['type']}")
        self.result_area.append(f"Created at: {result['created_at']}")
        
        for song in result['response_data']:
            self.result_area.append(f"\nTitle: {song['title']}")
            self.result_area.append(f"Audio URL: {song['audio_url']}")
            self.result_area.append(f"Image URL: {song['image_url']}")
            self.result_area.append(f"Duration: {song['duration']} seconds")
            self.result_area.append(f"Tags: {song['tags']}")
            self.result_area.append(f"Prompt: {song['prompt']}")
            self.result_area.append(f"Model: {song['model_name']}")
            self.result_area.append(f"Creation Time: {song['createTime']}")
            
            # Download and play the audio
            self.download_and_play_audio(song['audio_url'], song['title'])

        self.result_area.append("\nDebug: UdioPro result displayed")
        logging.info("UdioPro result displayed")

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

    def set_volume(self, value):
        volume = value / 100.0
        self.player.setVolume(int(volume * 100))

class UdioProWorker(QThread):
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, prompt, api_key):
        super().__init__()
        self.prompt = prompt
        self.api_key = api_key

    def run(self):
        try:
            url = "https://udioapi.pro/api/generate"
            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "prompt": self.prompt,
                "title": "Generated Song",
                "custom_mode": False,
                "make_instrumental": False,
                "model": "chirp-v3.5",
                "disable_callback": True,
                "token": self.api_key
            }

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_json = response.json()

            work_id = response_json.get('workId')
            if work_id:
                self.fetch_result(work_id)
            else:
                self.error_occurred.emit(f"Failed to get Work ID from UdioPro API. Response: {response_json}")

        except requests.RequestException as e:
            self.error_occurred.emit(f"Error calling UdioPro API: {str(e)}")

    def fetch_result(self, work_id):
        url = f"https://udioapi.pro/api/feed"
        params = {
            "workId": work_id
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        max_attempts = 30
        attempt = 0

        while attempt < max_attempts:
            try:
                response = requests.get(url, params=params, headers=headers)
                response.raise_for_status()
                result = response.json()

                if result['type'] == 'complete':
                    self.result_ready.emit(result)
                    break
                elif result['type'] in ['new', 'text', 'first']:
                    time.sleep(10)  # Wait for 10 seconds before next attempt
                else:
                    self.error_occurred.emit(f"Unexpected result type: {result['type']}")
                    break

            except requests.RequestException as e:
                self.error_occurred.emit(f"Error fetching UdioPro result: {str(e)}")
                break

            attempt += 1

        if attempt == max_attempts:
            self.error_occurred.emit("Maximum attempts reached while fetching UdioPro result")
