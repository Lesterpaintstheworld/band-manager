import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from welcome_screen import WelcomeScreen
# Import MainInterface will be done inside the after_splash method
from style import set_dark_theme

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class SyntheticBandManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        set_dark_theme(self.app)
        self.welcome_screen = None
        self.main_interface = None
        self.splash = QSplashScreen(QPixmap(resource_path("splash.png")))

    def run(self):
        self.splash.show()
        QTimer.singleShot(3000, self.after_splash)  # Show splash for 3 seconds
        sys.exit(self.app.exec_())

    def after_splash(self):
        self.splash.close()
        if self.band_name_exists():
            self.show_main_interface()
        else:
            self.welcome_screen = WelcomeScreen()
            self.welcome_screen.submitted.connect(self.show_main_interface)
            self.welcome_screen.show()

    def show_main_interface(self):
        from main_interface import MainInterface  # Import here to avoid circular import
        if self.welcome_screen:
            self.welcome_screen.close()
        self.main_interface = MainInterface()
        self.main_interface.change_band_name_signal.connect(self.change_band_name)
        self.main_interface.exit_game_signal.connect(self.exit_game)
        self.main_interface.show()

    def show_main_interface(self):
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
