from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLineEdit, QApplication, QMessageBox
from PyQt5.QtCore import pyqtSignal
from openai import OpenAI
import os
from dotenv import load_dotenv
from main import resource_path
from udio_wrapper import UdioWrapper

class ProductionTab(QWidget):
    production_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_api_key()
        self.load_system_prompt()
        self.load_udio_token()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area)

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)

        self.generate_song_button = QPushButton("Générer une chanson")
        self.generate_song_button.clicked.connect(self.generate_song)
        layout.addWidget(self.generate_song_button)

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
                    {"role": "user", "content": user_message}
                ],
                stream=True
            )
            
            self.chat_area.append("Assistant: ")
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    self.chat_area.insertPlainText(content)
                    QApplication.processEvents()
            
            self.update_production(full_response)
        except Exception as e:
            self.chat_area.append(f"Error sending message: {str(e)}")

    def update_production(self, new_content):
        current_content = self.result_area.toPlainText()
        updated_content = current_content + "\n\n" + new_content
        self.result_area.setPlainText(updated_content)
        self.production_updated.emit(updated_content)

    def generate_song(self):
        if not self.udio_wrapper:
            QMessageBox.critical(self, "Erreur", "Le token d'authentification Udio n'est pas configuré correctement.")
            return

        try:
            # You might want to get these values from user input or other parts of your application
            complete_song_sequence = self.udio_wrapper.create_complete_song(
                short_prompt="On a full moon night",
                extend_prompts=["the soft sound of the saxophone fills the air", "creating an atmosphere of mystery and romance"],
                outro_prompt="Thus ends this melody, leaving an echo of emotions in the heart",
                num_extensions=2,
                custom_lyrics_short="Short song lyrics here",
                custom_lyrics_extend=["Lyrics for first extension", "Lyrics for second extension"],
                custom_lyrics_outro="Outro lyrics here"
            )
            self.result_area.setPlainText(f"Complete song sequence generated and downloaded: {complete_song_sequence}")
            QMessageBox.information(self, "Succès", "La chanson a été générée avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur s'est produite lors de la génération de la chanson : {str(e)}")
