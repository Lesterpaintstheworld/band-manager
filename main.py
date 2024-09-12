import sys
import json
import os
import logging
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtGui import QPixmap, QPainter, QFont
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtWidgets import QApplication
from welcome_screen import WelcomeScreen
# Import MainInterface will be done inside the after_splash method
from style import set_dark_theme

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Load .env file
env_path = resource_path('.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    logging.info(f".env file loaded from {env_path}")
else:
    logging.warning(f".env file not found at {env_path}")

class SyntheticBandManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        set_dark_theme(self.app)
        self.welcome_screen = None
        self.main_interface = None
        splash_pixmap = QPixmap(resource_path("splash.png"))
        scaled_pixmap = splash_pixmap.scaled(QApplication.primaryScreen().size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        
        # Add version number to the splash screen
        painter = QPainter(scaled_pixmap)
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 12))
        painter.drawText(scaled_pixmap.rect().bottomRight() - QPoint(100, 30), "v0.1.0")
        painter.end()
        
        self.splash = QSplashScreen(scaled_pixmap)

    def run(self):
        self.splash.show()
        QTimer.singleShot(3000, self.after_splash)  # Show splash for 3 seconds
        sys.exit(self.app.exec_())

    def after_splash(self):
        self.splash.close()
        self.ensure_generated_songs_directory()
        if self.band_name_exists():
            self.show_main_interface()
        else:
            self.welcome_screen = WelcomeScreen()
            self.welcome_screen.submitted.connect(self.show_main_interface)
            self.welcome_screen.show()

    def ensure_generated_songs_directory(self):
        generated_songs_dir = 'generated_songs'
        if not os.path.exists(generated_songs_dir):
            os.makedirs(generated_songs_dir)
            logging.info(f"Created directory: {generated_songs_dir}")

    def show_main_interface(self):
        from main_interface import MainInterface
        if self.welcome_screen:
            self.welcome_screen.close()
        self.main_interface = MainInterface()
        self.main_interface.change_band_name_signal.connect(self.change_band_name)
        self.main_interface.exit_game_signal.connect(self.exit_game)
        self.main_interface.show()

    def change_band_name(self):
        self.main_interface.close()
        self.welcome_screen = WelcomeScreen(change_name=True)
        self.welcome_screen.submitted.connect(self.show_main_interface)
        self.welcome_screen.show()

    def exit_game(self):
        reply = QMessageBox.question(self.main_interface, 'Quitter', 'Êtes-vous sûr de vouloir quitter le jeu ?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.app.quit()

    def band_name_exists(self):
        if os.path.exists('band.json'):
            with open('band.json', 'r') as f:
                data = json.load(f)
                return 'name' in data and data['name']
        return False

if __name__ == "__main__":
    manager = SyntheticBandManager()
    manager.run()
