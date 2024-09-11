import sys
import json
import os
from PyQt5.QtWidgets import QApplication
from welcome_screen import WelcomeScreen
from main_interface import MainInterface

class SyntheticBandManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.welcome_screen = None
        self.main_interface = None

    def run(self):
        if self.band_name_exists():
            self.show_main_interface()
        else:
            self.welcome_screen = WelcomeScreen()
            self.welcome_screen.submitted.connect(self.show_main_interface)
            self.welcome_screen.show()
        sys.exit(self.app.exec_())

    def show_main_interface(self):
        if self.welcome_screen:
            self.welcome_screen.close()
        self.main_interface = MainInterface()
        self.main_interface.show()

    def band_name_exists(self):
        if os.path.exists('band.json'):
            with open('band.json', 'r') as f:
                data = json.load(f)
                return 'name' in data and data['name']
        return False

if __name__ == "__main__":
    manager = SyntheticBandManager()
    manager.run()
