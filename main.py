import sys
from PyQt5.QtWidgets import QApplication
from welcome_screen import WelcomeScreen

if __name__ == "__main__":
    app = QApplication(sys.argv)
    welcome_screen = WelcomeScreen()
    welcome_screen.show()
    sys.exit(app.exec_())
