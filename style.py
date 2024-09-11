from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

def set_dark_theme(app):
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(15, 15, 15))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(35, 35, 35))
    palette.setColor(QPalette.ToolTipBase, QColor(35, 35, 35))
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(35, 35, 35))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(200, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(150, 0, 0))
    palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(palette)
    app.setStyleSheet("""
        QWidget {
            background-color: #0f0f0f;
            color: #ffffff;
        }
        QTabWidget::pane {
            border: 1px solid #960000;
        }
        QTabBar::tab {
            background-color: #1f1f1f;
            color: #ffffff;
            padding: 8px 20px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #960000;
        }
        QPushButton {
            background-color: #960000;
            color: #ffffff;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #b20000;
        }
        QLineEdit {
            background-color: #1f1f1f;
            color: #ffffff;
            padding: 8px;
            border: 1px solid #960000;
            border-radius: 4px;
        }
        QTextEdit {
            background-color: #1f1f1f;
            color: #ffffff;
            border: 1px solid #960000;
            border-radius: 4px;
        }
    """)
