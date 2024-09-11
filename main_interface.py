from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QMenuBar, QAction
from PyQt5.QtCore import Qt, pyqtSignal
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

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Ajouter la barre de menu
        menubar = QMenuBar()
        layout.setMenuBar(menubar)

        # Créer le menu du groupe
        band_menu = menubar.addMenu(self.get_band_name())
        change_name_action = QAction('Changer le nom du groupe', self)
        change_name_action.triggered.connect(self.change_band_name)
        band_menu.addAction(change_name_action)

        # Ajouter l'option "Quitter le jeu"
        exit_action = QAction('Quitter le jeu', self)
        exit_action.triggered.connect(self.exit_game)
        menubar.addAction(exit_action)

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        tabs.setMovable(True)
        tabs.setDocumentMode(True)

        tabs.addTab(ConceptTab(), "Concept")
        tabs.addTab(LyricsTab(), "Lyrics")
        tabs.addTab(CompositionTab(), "Composition")
        tabs.addTab(ProductionTab(), "Production")
        tabs.addTab(VisualDesignTab(), "Visual Design")
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
