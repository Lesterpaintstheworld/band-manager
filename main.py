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
log_file = os.path.join(os.path.dirname(sys.executable), 'band_manager.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file,
    filemode='w'
)

# Add immediate logging to check if the program starts
logging.info("Program started")
print("Program started. Check the log file at:", log_file)

# Log system information
logging.info(f"Python version: {sys.version}")
logging.info(f"PyQt5 version: {Qt.PYQT_VERSION_STR}")
logging.info(f"Qt version: {Qt.QT_VERSION_STR}")
logging.info(f"Operating system: {sys.platform}")

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

class BandManager:
    def __init__(self):
        logging.info("Initializing BandManager")
        self.app = QApplication(sys.argv)
        logging.info("QApplication created")
        set_dark_theme(self.app)
        logging.info("Dark theme set")
        self.welcome_screen = None
        self.main_interface = None
        splash_pixmap = QPixmap(resource_path("splash.png"))
        logging.info(f"Splash image loaded from: {resource_path('splash.png')}")
        scaled_pixmap = splash_pixmap.scaled(QApplication.primaryScreen().size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        logging.info("Splash image scaled")
        
        # Add version number to the splash screen
        painter = QPainter(scaled_pixmap)
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 12))
        painter.drawText(scaled_pixmap.rect().bottomRight() - QPoint(100, 30), "v0.2.0")
        painter.end()
        logging.info("Version number added to splash screen")
        
        self.splash = QSplashScreen(scaled_pixmap)
        logging.info("Splash screen created")

    def run(self):
        logging.info("Application starting")
        self.splash.show()
        QTimer.singleShot(3000, self.after_splash)  # Show splash for 3 seconds
        logging.info("Entering main event loop")
        sys.exit(self.app.exec_())

    def after_splash(self):
        logging.info("Splash screen timer expired")
        self.splash.close()
        self.ensure_generated_songs_directory()
        if self.band_name_exists():
            logging.info("Band name exists, showing main interface")
            self.show_main_interface()
        else:
            logging.info("Band name doesn't exist, showing welcome screen")
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

def exception_hook(exctype, value, traceback):
    logging.error("Uncaught exception", exc_info=(exctype, value, traceback))
    sys.__excepthook__(exctype, value, traceback)

if __name__ == "__main__":
    sys.excepthook = exception_hook
    try:
        manager = BandManager()
        manager.run()
    except Exception as e:
        logging.exception("Fatal error in main loop")
