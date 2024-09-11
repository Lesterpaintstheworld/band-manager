from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QInputDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal
import json
import os

class SongManagementTab(QWidget):
    song_selected = pyqtSignal(str)
    song_deleted = pyqtSignal(str)

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
            songs.append({'title': title, 'lyrics': '', 'composition': '', 'visual_design': ''})
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
