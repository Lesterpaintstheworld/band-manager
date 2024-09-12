from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton

class ManagementTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Zone de texte pour afficher les informations du groupe
        self.info_area = QTextEdit()
        self.info_area.setReadOnly(True)
        layout.addWidget(self.info_area)

        # Champ de saisie pour les nouvelles informations
        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        # Bouton pour mettre à jour les informations
        self.update_button = QPushButton("Mettre à jour")
        self.update_button.clicked.connect(self.update_info)
        layout.addWidget(self.update_button)

        # Charger les informations existantes
        self.load_info()

    def load_info(self):
        # Charger les informations existantes depuis un fichier ou une base de données
        # Pour l'instant, nous utiliserons des informations factices
        info = "Nom du groupe : The Rockers\nStyle : Rock alternatif\nObjectif : Devenir le meilleur groupe de rock du monde"
        self.info_area.setPlainText(info)

    def update_info(self):
        # Mettre à jour les informations avec le texte saisi
        new_info = self.input_field.text()
        if new_info:
            current_info = self.info_area.toPlainText()
            updated_info = current_info + "\n" + new_info
            self.info_area.setPlainText(updated_info)
            self.input_field.clear()
            # Ici, vous pouvez ajouter du code pour sauvegarder les informations mises à jour
