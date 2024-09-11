from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
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
        self.load_system_prompt()

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

    def load_api_key(self):
        load_dotenv()
        api_key = os.getenv('AIDER_API_KEY')
        if not api_key:
            self.chat_area.append("Erreur : Clé API Aider non trouvée dans le fichier .env. Veuillez ajouter AIDER_API_KEY à votre fichier .env.")

    def load_system_prompt(self):
        try:
            with open('prompts/concept.md', 'r', encoding='utf-8') as f:
                self.system_prompt = f.read()
        except FileNotFoundError:
            self.system_prompt = "Vous êtes un assistant créatif pour aider à développer des concepts de chansons."
            self.chat_area.append("Attention : Le fichier prompts/concept.md n'a pas été trouvé. Utilisation d'un prompt par défaut.")

    def send_message(self):
        user_message = self.input_field.text()
        self.chat_area.append(f"Vous : {user_message}")
        self.input_field.clear()

        try:
            # Ici, vous devrez implémenter une nouvelle logique pour envoyer le message et recevoir une réponse
            # Par exemple, vous pourriez utiliser une autre bibliothèque ou API
            response = "Réponse simulée de l'assistant"
            self.chat_area.append("Assistant : " + response)
            self.update_concept(response)
        except Exception as e:
            self.chat_area.append(f"Erreur : {str(e)}")

    def update_concept(self, new_content):
        current_concept = self.result_area.toPlainText()
        updated_concept = current_concept + "\n\n" + new_content
        self.result_area.setPlainText(updated_concept)
        self.concept_updated.emit(updated_concept)
        
        # Sauvegarder le concept dans concept.md
        with open('concept.md', 'w', encoding='utf-8') as f:
            f.write(updated_concept)
