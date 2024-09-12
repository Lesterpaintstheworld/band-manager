from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QMenuBar, QAction, QLabel, QHBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QPushButton
from management import ManagementTab
from concept import ConceptTab
from lyrics import LyricsTab
from composition import CompositionTab
from production import ProductionTab
from visual_design import VisualDesignTab
from concert import ConcertTab
from song_management import SongManagementTab
from critique import CritiqueTab
import os
import sys
from dotenv import load_dotenv

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
        self.setWindowTitle('Band Manager')
        self.showFullScreen()

        # Appliquer le style CSS
        style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'style.css')
        if os.path.exists(style_path):
            with open(style_path, 'r') as f:
                self.setStyleSheet(f.read())
        else:
            print(f"Warning: style.css not found at {style_path}")

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Add menu bar
        menubar = QMenuBar()
        main_layout.addWidget(menubar)


        # Créer un layout horizontal pour le titre et le bouton de fermeture
        top_layout = QHBoxLayout()
        
        # Ajouter le titre du jeu
        title_label = QLabel("Band Manager")
        title_label.setObjectName("game-title")
        top_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        
        # Ajouter le bouton de fermeture
        close_button = QPushButton("×")
        close_button.setObjectName("close-button")
        close_button.clicked.connect(self.close)
        top_layout.addWidget(close_button, alignment=Qt.AlignRight)
        
        main_layout.addLayout(top_layout)

        # Ajouter la barre de menu
        menubar = QMenuBar()
        menubar.setObjectName("game-menu")
        main_layout.addWidget(menubar)

        # Créer le menu du groupe
        band_menu = menubar.addMenu(self.get_band_name())
        change_name_action = QAction(QIcon('icons/edit.png'), 'Change band name', self)
        change_name_action.triggered.connect(self.change_band_name)
        band_menu.addAction(change_name_action)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("game-tabs")
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)

        self.song_management_tab = SongManagementTab()
        self.management_tab = ManagementTab()
        self.concept_tab = ConceptTab()
        self.lyrics_tab = LyricsTab()
        self.composition_tab = CompositionTab()
        self.production_tab = ProductionTab()
        self.production_tab.send_button.clicked.connect(self.production_tab.handle_user_prompt)
        self.visual_design_tab = VisualDesignTab()
        self.concert_tab = ConcertTab()
        self.critique_tab = CritiqueTab()

        self.tabs.addTab(self.song_management_tab, "Song Management")
        self.tabs.addTab(self.management_tab, "Management")
        self.tabs.addTab(self.concept_tab, "Concept")
        self.tabs.addTab(self.lyrics_tab, "Lyrics")
        self.tabs.addTab(self.composition_tab, "Composition")
        self.tabs.addTab(self.production_tab, "Production")
        self.tabs.addTab(self.visual_design_tab, "Visual Design")
        self.tabs.addTab(self.critique_tab, "Critique")
        self.tabs.addTab(self.concert_tab, "Concert")

        self.song_management_tab.song_selected.connect(self.load_song)
        self.song_management_tab.song_deleted.connect(self.on_song_deleted)
        self.song_management_tab.song_saved.connect(self.on_song_saved)
        self.song_management_tab.song_renamed.connect(self.on_song_renamed)

        main_layout.addWidget(self.tabs)

    def reset_chats(self):
        self.concept_tab.chat_area.clear()
        self.lyrics_tab.chat_area.clear()
        self.composition_tab.chat_area.clear()
        self.production_tab.chat_area.clear()
        self.visual_design_tab.chat_area.clear()

    def get_band_name(self):
        import json
        with open('band.json', 'r') as f:
            data = json.load(f)
            return data.get('name', 'Unnamed Band')

    def change_band_name(self):
        self.change_band_name_signal.emit()

    def new_song(self):
        self.reset_chats()
        self.new_song_signal.emit()

    def load_song(self, song_title):
        song_folder = os.path.join('songs', song_title)
        if os.path.exists(song_folder):
            try:
                # Load concept
                with open(os.path.join(song_folder, 'concept.md'), 'r', encoding='utf-8') as f:
                    self.concept_tab.result_area.setPlainText(f.read())

                # Load lyrics
                with open(os.path.join(song_folder, 'lyrics.md'), 'r', encoding='utf-8') as f:
                    self.lyrics_tab.result_area.setPlainText(f.read())

                # Load composition
                with open(os.path.join(song_folder, 'composition.md'), 'r', encoding='utf-8') as f:
                    self.composition_tab.result_area.setPlainText(f.read())

                # Load visual design
                with open(os.path.join(song_folder, 'visual_design.md'), 'r', encoding='utf-8') as f:
                    self.visual_design_tab.result_area.setPlainText(f.read())

                # Switch to the Concept tab
                self.tabs.setCurrentWidget(self.concept_tab)
            except Exception as e:
                QMessageBox.warning(self, "Load Failed", f"An error occurred while loading the song: {str(e)}")
        else:
            QMessageBox.warning(self, "Load Failed", f"Song folder for '{song_title}' not found.")

    def save_song(self):
        current_song = self.song_management_tab.get_current_song()
        if current_song:
            current_song['concept'] = self.concept_tab.result_area.toPlainText()
            current_song['lyrics'] = self.lyrics_tab.result_area.toPlainText()
            current_song['composition'] = self.composition_tab.result_area.toPlainText()
            current_song['visual_design'] = self.visual_design_tab.result_area.toPlainText()
            self.song_management_tab.update_current_song(current_song)
            self.song_management_tab.save_song()
        else:
            QMessageBox.warning(self, "Save Failed", "No song is currently selected.")

    def on_song_deleted(self, song_title):
        # Clear all tabs when a song is deleted
        self.concept_tab.result_area.clear()
        self.lyrics_tab.result_area.clear()
        self.composition_tab.result_area.clear()
        self.visual_design_tab.result_area.clear()

    def on_song_saved(self, song_title):
        QMessageBox.information(self, "Save Successful", f"Song '{song_title}' has been saved.")

    def on_song_renamed(self, old_title, new_title):
        QMessageBox.information(self, "Rename Successful", f"Song '{old_title}' has been renamed to '{new_title}'.")


