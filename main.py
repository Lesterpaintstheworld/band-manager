import sys
from PyQt5.QtWidgets import QApplication
from welcome_screen import WelcomeScreen
from main_interface import MainInterface

class SyntheticBandManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.welcome_screen = WelcomeScreen()
        self.main_interface = None

    def run(self):
        self.welcome_screen.submitted.connect(self.show_main_interface)
        self.welcome_screen.show()
        sys.exit(self.app.exec_())

    def show_main_interface(self):
        self.welcome_screen.close()
        self.main_interface = MainInterface()
        self.main_interface.show()

if __name__ == "__main__":
    manager = SyntheticBandManager()
    manager.run()
