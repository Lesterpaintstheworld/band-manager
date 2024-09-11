from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QInputDialog, QMessageBox, QFileDialog
from PyQt5.QtCore import pyqtSignal
import json
import os
import shutil

class SongManagementTab(QWidget):
    song_selected = pyqtSignal(str)
    song_deleted = pyqtSignal(str)
    song_saved = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_songs()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.song_list = QListWidget()
        layout.addWidget(self.song_list)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        self.new_song_button = QPushButton("New Song")
        self.new_song_button.clicked.connect(self.create_new_song)
        button_layout.addWidget(self.new_song_button)

        self.delete_song_button = QPushButton("Delete Song")
        self.delete_song_button.clicked.connect(self.delete_song)
        button_layout.addWidget(self.delete_song_button)

        self.save_song_button = QPushButton("Save Song")
        self.save_song_button.clicked.connect(self.save_song)
        button_layout.addWidget(self.save_song_button)

        self.song_list.itemClicked.connect(self.on_song_selected)

    def load_songs(self):
        self.song_list.clear()
        if os.path.exists('songs.json'):
            with open('songs.json', 'r') as f:
                songs = json.load(f)
                for song in songs:
                    self.song_list.addItem(song['title'])

    def create_new_song(self):
        title, ok = QInputDialog.getText(self, 'New Song', 'Enter song title:')
        if ok and title:
            songs = self.get_songs()
            songs.append({'title': title, 'lyrics': '', 'composition': '', 'visual_design': '', 'concept': ''})
            self.save_songs(songs)
            self.load_songs()
            self.song_selected.emit(title)

    def delete_song(self):
        current_item = self.song_list.currentItem()
        if current_item:
            reply = QMessageBox.question(self, 'Delete Song', 
                                         f"Are you sure you want to delete '{current_item.text()}'?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                songs = self.get_songs()
                songs = [song for song in songs if song['title'] != current_item.text()]
                self.save_songs(songs)
                self.load_songs()
                self.song_deleted.emit(current_item.text())

                # Delete the song folder if it exists
                song_folder = os.path.join('songs', current_item.text())
                if os.path.exists(song_folder):
                    shutil.rmtree(song_folder)

    def on_song_selected(self, item):
        self.song_selected.emit(item.text())

    def get_songs(self):
        if os.path.exists('songs.json'):
            with open('songs.json', 'r') as f:
                return json.load(f)
        return []

    def save_songs(self, songs):
        with open('songs.json', 'w') as f:
            json.dump(songs, f)

    def get_current_song(self):
        current_item = self.song_list.currentItem()
        if current_item:
            songs = self.get_songs()
            for song in songs:
                if song['title'] == current_item.text():
                    return song
        return None

    def update_current_song(self, updated_song):
        songs = self.get_songs()
        for i, song in enumerate(songs):
            if song['title'] == updated_song['title']:
                songs[i] = updated_song
                break
        self.save_songs(songs)

    def save_song(self):
        current_song = self.get_current_song()
        if current_song:
            song_folder = os.path.join('songs', current_song['title'])
            os.makedirs(song_folder, exist_ok=True)

            # Save concept
            with open(os.path.join(song_folder, 'concept.md'), 'w', encoding='utf-8') as f:
                f.write(current_song.get('concept', ''))

            # Save lyrics
            with open(os.path.join(song_folder, 'lyrics.md'), 'w', encoding='utf-8') as f:
                f.write(current_song.get('lyrics', ''))

            # Save composition
            with open(os.path.join(song_folder, 'composition.md'), 'w', encoding='utf-8') as f:
                f.write(current_song.get('composition', ''))

            # Save visual design
            with open(os.path.join(song_folder, 'visual_design.md'), 'w', encoding='utf-8') as f:
                f.write(current_song.get('visual_design', ''))

            self.song_saved.emit(current_song['title'])
            QMessageBox.information(self, "Save Successful", f"Song '{current_song['title']}' has been saved.")
        else:
            QMessageBox.warning(self, "Save Failed", "No song is currently selected.")
