from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QMenuBar, QAction, QLabel, QHBoxLayout, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QPushButton
from concept import ConceptTab
from lyrics import LyricsTab
from composition import CompositionTab
from production import ProductionTab
from visual_design import VisualDesignTab
from concert import ConcertTab
from song_management import SongManagementTab

class MainInterface(QWidget):
    change_band_name_signal = pyqtSignal()
    new_song_signal = pyqtSignal()
    load_song_signal = pyqtSignal(str)
    save_song_signal = pyqtSignal(str)
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

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Add menu bar
        menubar = QMenuBar()
        main_layout.addWidget(menubar)

        # Add Song menu
        song_menu = menubar.addMenu('Song')
        
        # Add New action
        new_action = QAction('New', self)
        new_action.triggered.connect(self.new_song)
        song_menu.addAction(new_action)

        # Add Load action
        load_action = QAction('Load', self)
        load_action.triggered.connect(self.load_song)
        song_menu.addAction(load_action)

        # Add Save action
        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save_song)
        song_menu.addAction(save_action)

        layout = QVBoxLayout()
        main_layout.addLayout(layout)

        # Ajouter le titre du jeu
        title_label = QLabel("Synthetic Band Manager")
        title_label.setObjectName("game-title")
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # Créer un layout horizontal pour le titre et le bouton de fermeture
        top_layout = QHBoxLayout()
        
        # Ajouter le titre du jeu
        title_label = QLabel("Synthetic Band Manager")
        title_label.setObjectName("game-title")
        top_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        
        # Ajouter le bouton de fermeture
        close_button = QPushButton("×")
        close_button.setObjectName("close-button")
        close_button.clicked.connect(self.close)
        top_layout.addWidget(close_button, alignment=Qt.AlignRight)
        
        layout.addLayout(top_layout)

        # Ajouter la barre de menu
        menubar = QMenuBar()
        menubar.setObjectName("game-menu")
        layout.addWidget(menubar)

        # Créer le menu du groupe
        band_menu = menubar.addMenu(self.get_band_name())
        change_name_action = QAction(QIcon('icons/edit.png'), 'Changer le nom du groupe', self)
        change_name_action.triggered.connect(self.change_band_name)
        band_menu.addAction(change_name_action)

        tabs = QTabWidget()
        tabs.setObjectName("game-tabs")
        tabs.setTabPosition(QTabWidget.North)
        tabs.setMovable(True)
        tabs.setDocumentMode(True)

        self.song_management_tab = SongManagementTab()
        tabs.addTab(self.song_management_tab, "Song Management")
        tabs.addTab(ConceptTab(), "Concept")
        tabs.addTab(LyricsTab(), "Paroles")
        tabs.addTab(CompositionTab(), "Composition")
        tabs.addTab(ProductionTab(), "Production")
        tabs.addTab(VisualDesignTab(), "Design Visuel")
        tabs.addTab(ConcertTab(), "Concert")

        self.song_management_tab.song_selected.connect(self.load_song)
        self.song_management_tab.song_deleted.connect(self.on_song_deleted)

        layout.addWidget(tabs)

    def get_band_name(self):
        import json
        with open('band.json', 'r') as f:
            data = json.load(f)
            return data.get('name', 'Groupe sans nom')

    def change_band_name(self):
        self.change_band_name_signal.emit()

    def new_song(self):
        self.new_song_signal.emit()

    def load_song(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Song", "", "JSON Files (*.json)")
        if file_name:
            self.load_song_signal.emit(file_name)

    def save_song(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Song", "", "JSON Files (*.json)")
        if file_name:
            self.save_song_signal.emit(file_name)

    def load_song(self, song_title):
        # Implement logic to load the selected song into the tabs
        pass

    def on_song_deleted(self, song_title):
        # Implement logic to handle song deletion (e.g., clear tabs if the current song was deleted)
        pass

