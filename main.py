import sys
import json
import os
import logging
import traceback
import argparse
from dotenv import load_dotenv

print(f"Répertoire de travail actuel : {os.getcwd()}")
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Démarrage du programme")

# Ajout du chemin du répertoire courant au sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

logging.info(f"Tentative d'importation de NumPy. sys.path: {sys.path}")
try:
    import numpy as np
    logging.info(f"NumPy importé avec succès. Version: {np.__version__}")
except ImportError as e:
    logging.error(f"Erreur lors de l'importation de NumPy: {e}")
    logging.info("Tentative d'ajout du répertoire parent au sys.path")
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    logging.info(f"Nouveau sys.path après ajout du répertoire parent: {sys.path}")
    try:
        import numpy as np
        logging.info(f"NumPy importé avec succès après ajout du répertoire parent. Version: {np.__version__}")
    except ImportError as e:
        logging.error(f"Échec de l'importation de NumPy même après ajout du répertoire parent: {e}")
        logging.error("Contenu du répertoire courant:")
        for item in os.listdir(current_dir):
            logging.error(f"- {item}")
        logging.error("Contenu du répertoire parent:")
        for item in os.listdir(parent_dir):
            logging.error(f"- {item}")
        sys.exit(1)
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtGui import QPixmap, QPainter, QFont
from PyQt5.QtCore import Qt, QTimer, QPoint, PYQT_VERSION_STR, QT_VERSION_STR
import PyQt5.QtCore
from PyQt5.QtWidgets import QApplication
from welcome_screen import WelcomeScreen
# Import MainInterface will be done inside the after_splash method
from style import set_dark_theme

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Band Manager Application')
parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
args = parser.parse_args()

# Configure logging
if getattr(sys, 'frozen', False):
    # We are running in a bundle
    bundle_dir = sys._MEIPASS
else:
    # We are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

log_file = os.path.join(bundle_dir, 'band_manager.log')
logging.basicConfig(
    level=logging.DEBUG if args.verbose else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file,
    filemode='w'
)

# Add a console handler to see logs in console as well
console = logging.StreamHandler()
console.setLevel(logging.DEBUG if args.verbose else logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Add immediate logging to check if the program starts
logging.info("Program started")
print("Program started. Check the log file at:", log_file)
if args.verbose:
    print("Verbose logging enabled")

# Log system information
logging.info(f"Python version: {sys.version}")
logging.info(f"PyQt5 version: {PyQt5.QtCore.PYQT_VERSION_STR}")
logging.info(f"Qt version: {PyQt5.QtCore.QT_VERSION_STR}")
logging.info(f"Operating system: {sys.platform}")
logging.info(f"Bundle directory: {bundle_dir}")

# Add more detailed logging
logging.info("Importing required modules...")
logging.info("Modules imported successfully")

# Log environment variables
logging.info("Environment variables:")
for key, value in os.environ.items():
    logging.info(f"{key}: {value}")

# Check if running as executable
if getattr(sys, 'frozen', False):
    logging.info("Running as executable")
else:
    logging.info("Running as script")

# Log current working directory
logging.info(f"Current working directory: {os.getcwd()}")

# Log contents of the bundle directory
logging.info(f"Contents of bundle directory ({bundle_dir}):")
for item in os.listdir(bundle_dir):
    logging.info(f"- {item}")

# Set up global exception handler
def global_exception_handler(exctype, value, tb):
    logging.error("Uncaught exception", exc_info=(exctype, value, tb))
    traceback_str = ''.join(traceback.format_tb(tb))
    logging.error(f"Traceback:\n{traceback_str}")
    error_msg = f"An unexpected error occurred:\n{str(value)}\n\nPlease check the log file for more details."
    logging.error(error_msg)
    print(error_msg)  # Print to console as well
    # Commentez la ligne suivante pour éviter que l'application ne se ferme immédiatement
    # QMessageBox.critical(None, "Error", error_msg)

sys.excepthook = global_exception_handler

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
    # Fallback to environment variables
    logging.info("Attempting to use environment variables")
    for key in ['OPENAI_API_KEY', 'UDIOPRO_API_KEY']:
        if os.environ.get(key):
            logging.info(f"{key} found in environment variables")
        else:
            logging.warning(f"{key} not found in environment variables")

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
        logging.info("Création de l'instance BandManager")
        manager = BandManager()
        logging.info("Lancement de l'application")
        manager.run()
    except Exception as e:
        logging.exception("Erreur fatale dans la boucle principale")
        print(f"Une erreur fatale s'est produite : {str(e)}")
        input("Appuyez sur Entrée pour quitter...")
