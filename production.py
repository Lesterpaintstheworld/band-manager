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
import time
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
        self.load_suno_api()

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

    def load_suno_api(self):
        load_dotenv()
        self.suno_api_url = 'https://api.suno.ai'
        self.suno_cookie = os.getenv('SUNO_COOKIE')
        if not self.suno_cookie:
            self.chat_area.append("Error: Suno API Cookie not found in .env file.")
            self.chat_area.append("Please add SUNO_COOKIE to your .env file.")
            self.suno_api = None
        else:
            max_retries = 3
            retry_delay = 5  # seconds
            for attempt in range(max_retries):
                try:
                    headers = {'Cookie': self.suno_cookie}
                    response = requests.get(f"{self.suno_api_url}/api/get_limit", headers=headers, timeout=10)
                    if response.status_code == 200:
                        self.chat_area.append("Suno API connection initialized successfully.")
                        self.suno_api = True
                        break
                    elif response.status_code == 503:
                        if attempt < max_retries - 1:
                            self.chat_area.append(f"Suno API temporarily unavailable. Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                        else:
                            raise Exception(f"Failed to connect to Suno API after {max_retries} attempts. Status code: 503")
                    else:
                        raise Exception(f"Failed to connect to Suno API. Status code: {response.status_code}")
                except requests.RequestException as e:
                    if attempt < max_retries - 1:
                        self.chat_area.append(f"Network error. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        self.chat_area.append(f"Error initializing Suno API connection: {str(e)}")
                        self.chat_area.append("Please check your network connection and Suno API URL in the .env file.")
                        self.suno_api = None
            if self.suno_api is None:
                self.chat_area.append("Failed to initialize Suno API after multiple attempts.")

    def load_suno_api(self):
        load_dotenv()
        self.suno_api_url = os.getenv('SUNO_API_URL', 'https://api.suno.ai')
        self.suno_cookie = os.getenv('SUNO_COOKIE')
        if not self.suno_api_url or not self.suno_cookie:
            self.chat_area.append("Error: Suno API URL or Cookie not found in .env file.")
            self.chat_area.append("Please add SUNO_API_URL and SUNO_COOKIE to your .env file.")
            self.suno_api = None
        else:
            try:
                headers = {'Cookie': self.suno_cookie}
                response = requests.get(f"{self.suno_api_url}/api/get_limit", headers=headers)
                if response.status_code == 200:
                    self.chat_area.append("Suno API connection initialized successfully.")
                    self.suno_api = True
                else:
                    raise Exception(f"Failed to connect to Suno API. Status code: {response.status_code}")
            except Exception as e:
                self.chat_area.append(f"Error initializing Suno API connection: {str(e)}")
                self.chat_area.append("Please check your Suno API URL and Cookie in the .env file.")
                self.suno_api = None

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
        try:
            self.result_area.clear()
            self.result_area.append("Generating song...")
            self.chat_area.append("Starting song generation...")
            logger.info(f"Starting song generation with prompt: {gpt_response['short_prompt']}")

            start_time = time.time()
            # Generate the song
            try:
                song_data = self.udio_wrapper.song_generator.generate_song(
                    song_title=gpt_response['short_prompt'],
                    song_description="Generated song description"
                )
                logger.info("Udio generate_song method called successfully")
            except Exception as udio_error:
                logger.error(f"Error in Udio generate_song method: {str(udio_error)}", exc_info=True)
                raise Exception(f"Udio song generation failed: {str(udio_error)}")

            end_time = time.time()
            generation_time = end_time - start_time
            logger.info(f"Song generation completed in {generation_time:.2f} seconds")

            # Log the Udio API response
            logger.info(f"Udio API response type: {type(song_data)}")
            logger.info(f"Udio API response length: {len(song_data) if song_data else 'N/A'}")
            if song_data:
                logger.info(f"First 100 bytes of Udio API response: {song_data[:100]}")
            else:
                logger.warning("Udio API response is empty or None")

            self.chat_area.append(f"Udio API response received. Length: {len(song_data) if song_data else 'N/A'}")

            if not song_data:
                logger.error("The generated song data is empty.")
                raise Exception("The generated song data is empty.")

            # Save the audio file in the songs/ folder
            song_filename = f"song_{int(time.time())}.mp3"
            song_path = os.path.join("songs", song_filename)
            os.makedirs("songs", exist_ok=True)
            
            logger.info(f"Saving song to {song_path}")
            with open(song_path, 'wb') as f:
                f.write(song_data)
            logger.info(f"Song saved successfully. File size: {len(song_data)} bytes")
            
            self.result_area.clear()
            self.result_area.append(f"Song generated and saved: {song_path}")
            self.chat_area.append(f"Song generated and saved: {song_path}")
            
            # Wait for a short time to ensure the file is fully written
            time.sleep(1)
            
            # Play the song in the audio player
            logger.info("Attempting to play the generated song")
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(song_path)))
            self.player.error.connect(self.handle_player_error)
            self.player.play()
            
            # Wait for the player to be ready
            while self.player.state() == QMediaPlayer.LoadingMedia:
                QApplication.processEvents()
            
            if self.player.error() == QMediaPlayer.NoError:
                logger.info("Song playback started successfully")
                QMessageBox.information(self, "Success", "The song has been generated successfully and is now playing.")
            else:
                logger.warning(f"Playback issue detected. Player error: {self.player.error()}")
                QMessageBox.warning(self, "Playback Issue", "The song was generated successfully, but there might be an issue with playback. You can find the audio file at: " + song_path)
            
            # Emit the production_updated signal with the new content
            self.production_updated.emit(song_path)
        except Exception as e:
            error_message = f"An error occurred while generating the song: {str(e)}"
            self.chat_area.append(error_message)
            self.result_area.append(f"Error: {str(e)}")
            logger.error(f"Song generation error: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Error", error_message)

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
        
        # Check if the file exists and is readable
        song_path = self.player.media().canonicalUrl().toLocalFile()
        if not os.path.exists(song_path):
            self.chat_area.append(f"Error: The audio file does not exist at {song_path}")
            logger.error(f"Audio file not found: {song_path}")
        elif not os.access(song_path, os.R_OK):
            self.chat_area.append(f"Error: The audio file is not readable at {song_path}")
            logger.error(f"Audio file not readable: {song_path}")
        else:
            file_size = os.path.getsize(song_path)
            self.chat_area.append(f"Audio file exists and is readable. File size: {file_size} bytes")
            logger.info(f"Audio file info: {song_path}, Size: {file_size} bytes")

        # Try to get more information about the media
        media_status = self.player.mediaStatus()
        self.chat_area.append(f"Media status: {media_status}")
        logger.info(f"Media status: {media_status}")

        # Check supported audio formats
        supported_formats = QMediaPlayer.supportedMimeTypes()
        self.chat_area.append(f"Supported audio formats: {', '.join(supported_formats)}")
        logger.info(f"Supported audio formats: {', '.join(supported_formats)}")

    def generate_song(self, gpt_response):
        try:
            self.result_area.clear()
            self.result_area.append("Generating song...")
            self.chat_area.append("Starting song generation...")
            logger.info(f"Starting song generation with prompt: {gpt_response['short_prompt']}")

            start_time = time.time()
            # Generate the song using Suno API
            payload = {
                "prompt": gpt_response['short_prompt'],
                "make_instrumental": False,
                "wait_audio": False
            }
            headers = {'Cookie': self.suno_cookie}
            response = requests.post(f"{self.suno_api_url}/api/generate", json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for non-200 status codes
            
            data = response.json()
            end_time = time.time()
            generation_time = end_time - start_time
            logger.info(f"Song generation request completed in {generation_time:.2f} seconds")

            # Log the Suno API response
            logger.info(f"Suno API response: {data}")

            if not isinstance(data, list) or len(data) < 2:
                raise ValueError("Unexpected response format from Suno API")

            self.chat_area.append(f"Suno API response received. IDs: {data[0]['id']}, {data[1]['id']}")

            # Wait for the audio to be ready
            ids = f"{data[0]['id']},{data[1]['id']}"
            audio_urls = []
            for _ in range(60):  # Wait for up to 5 minutes
                response = requests.get(f"{self.suno_api_url}/api/get?ids={ids}", headers={'Cookie': self.suno_cookie})
                response.raise_for_status()
                audio_info = response.json()
                if all(info['status'] == 'streaming' for info in audio_info):
                    audio_urls = [info['audio_url'] for info in audio_info if 'audio_url' in info]
                    break
                time.sleep(5)

            if not audio_urls:
                raise Exception("Timeout: Audio generation took too long or no audio URLs were provided.")

            # Download and save the audio files
            song_paths = []
            for i, url in enumerate(audio_urls):
                song_filename = f"song_{int(time.time())}_{i}.mp3"
                song_path = os.path.join("songs", song_filename)
                os.makedirs("songs", exist_ok=True)
                
                response = requests.get(url)
                response.raise_for_status()
                
                with open(song_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Song part {i+1} saved successfully at: {song_path}")
                song_paths.append(song_path)
            
            self.result_area.clear()
            self.result_area.append(f"Songs generated and saved: {', '.join(song_paths)}")
            self.chat_area.append(f"Songs generated and saved: {', '.join(song_paths)}")
            
            # Play the first song in the audio player
            if song_paths:
                logger.info("Attempting to play the generated song")
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(song_paths[0])))
                self.player.error.connect(self.handle_player_error)
                self.player.play()
                
                if self.player.error() == QMediaPlayer.NoError:
                    logger.info("Song playback started successfully")
                    QMessageBox.information(self, "Success", "The songs have been generated successfully and the first one is now playing.")
                else:
                    logger.warning(f"Playback issue detected. Player error: {self.player.error()}")
                    QMessageBox.warning(self, "Playback Issue", "The songs were generated successfully, but there might be an issue with playback. You can find the audio files at: " + ', '.join(song_paths))
                
                # Emit the production_updated signal with the new content
                self.production_updated.emit(song_paths[0])
            else:
                logger.warning("No songs were generated")
                QMessageBox.warning(self, "Generation Issue", "No songs were generated. Please try again.")
        except requests.RequestException as e:
            error_message = f"Network error occurred while communicating with Suno API: {str(e)}"
            self.chat_area.append(error_message)
            self.result_area.append(f"Error: {str(e)}")
            logger.error(f"Suno API communication error: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Network Error", error_message)
        except Exception as e:
            error_message = f"An error occurred while generating the song: {str(e)}"
            self.chat_area.append(error_message)
            self.result_area.append(f"Error: {str(e)}")
            logger.error(f"Song generation error: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Error", error_message)
