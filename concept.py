from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
import openai
from dotenv import load_dotenv
import os

class ConceptTab(QWidget):
    concept_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_api_key()
        self.current_stream = None
        self.stream_buffer = ""

    def initUI(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Chat area
        chat_layout = QVBoxLayout()
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        chat_layout.addWidget(self.chat_area)

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Envoyer")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        chat_layout.addLayout(input_layout)
        layout.addLayout(chat_layout)

        # Concept display area
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)

        # Timer for updating the stream
        self.stream_timer = QTimer()
        self.stream_timer.timeout.connect(self.update_stream)
        self.stream_timer.start(100)  # Update every 100ms

    def load_api_key(self):
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            self.chat_area.append("Erreur : Clé API OpenAI non trouvée dans le fichier .env. Veuillez ajouter OPENAI_API_KEY à votre fichier .env.")

    def send_message(self):
        user_message = self.input_field.text()
        self.chat_area.append(f"Vous : {user_message}")
        self.input_field.clear()

        try:
            self.current_stream = openai.ChatCompletion.create(
                model="gpt-4",  # Assurez-vous que ce modèle est disponible pour votre compte
                messages=[
                    {"role": "system", "content": "Vous êtes un assistant créatif pour aider à développer des concepts de chansons."},
                    {"role": "user", "content": user_message}
                ],
                stream=True
            )
            self.chat_area.append("Assistant : ")
            self.stream_buffer = ""
        except Exception as e:
            self.chat_area.append(f"Erreur : {str(e)}")

    def update_stream(self):
        if self.current_stream:
            try:
                for chunk in self.current_stream:
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        if 'delta' in chunk['choices'][0] and 'content' in chunk['choices'][0]['delta']:
                            content = chunk['choices'][0]['delta']['content']
                            self.stream_buffer += content
                            self.chat_area.append(content)
                            QApplication.processEvents()  # Permet à l'interface de se mettre à jour

                # Fin du stream
                self.current_stream = None
                self.update_concept(self.stream_buffer)
            except Exception as e:
                self.chat_area.append(f"Erreur lors du streaming : {str(e)}")
                self.current_stream = None

    def update_concept(self, new_content):
        current_concept = self.result_area.toPlainText()
        updated_concept = current_concept + "\n\n" + new_content
        self.result_area.setPlainText(updated_concept)
        self.concept_updated.emit(updated_concept)
        
        # Sauvegarder le concept dans concept.md
        with open('concept.md', 'w', encoding='utf-8') as f:
            f.write(updated_concept)
