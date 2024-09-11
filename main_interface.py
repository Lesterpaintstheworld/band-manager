from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QMenuBar, QAction, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from concept import ConceptTab
from lyrics import LyricsTab
from composition import CompositionTab
from production import ProductionTab
from visual_design import VisualDesignTab
from concert import ConcertTab

class MainInterface(QWidget):
    change_band_name_signal = pyqtSignal()
    exit_game_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Synthetic Band Manager')
        self.showFullScreen()

        # Appliquer le style CSS
        with open('style.css', 'r') as f:
            self.setStyleSheet(f.read())

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Ajouter le titre du jeu
        title_label = QLabel("Synthetic Band Manager")
        title_label.setObjectName("game-title")
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # Ajouter la barre de menu
        menubar = QMenuBar()
        menubar.setObjectName("game-menu")
        layout.setMenuBar(menubar)

        # Créer le menu du groupe
        band_menu = menubar.addMenu(self.get_band_name())
        change_name_action = QAction(QIcon('icons/edit.png'), 'Changer le nom du groupe', self)
        change_name_action.triggered.connect(self.change_band_name)
        band_menu.addAction(change_name_action)

        # Ajouter l'option "Quitter le jeu"
        exit_action = QAction(QIcon('icons/exit.png'), 'Quitter le jeu', self)
        exit_action.triggered.connect(self.exit_game)
        menubar.addAction(exit_action)

        tabs = QTabWidget()
        tabs.setObjectName("game-tabs")
        tabs.setTabPosition(QTabWidget.North)
        tabs.setMovable(True)
        tabs.setDocumentMode(True)

        tabs.addTab(ConceptTab(), "Concept")
        tabs.addTab(LyricsTab(), "Paroles")
        tabs.addTab(CompositionTab(), "Composition")
        tabs.addTab(ProductionTab(), "Production")
        tabs.addTab(VisualDesignTab(), "Design Visuel")
        tabs.addTab(ConcertTab(), "Concert")

        layout.addWidget(tabs)

    def get_band_name(self):
        import json
        with open('band.json', 'r') as f:
            data = json.load(f)
            return data.get('name', 'Groupe sans nom')

    def change_band_name(self):
        self.change_band_name_signal.emit()

    def exit_game(self):
        self.exit_game_signal.emit()
