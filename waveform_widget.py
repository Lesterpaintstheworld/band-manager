import os
import sys
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen
from pydub import AudioSegment
import statistics

class WaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.waveform_data = []
        self.current_position = 0
        self.duration = 0
        self.setMinimumHeight(100)

    def load_audio(self, file_path):
        audio = AudioSegment.from_file(file_path)
        self.waveform_data = audio.get_array_of_samples()
        self.duration = len(audio)
        self.update()

    def set_duration(self, duration):
        self.duration = duration

    def update_position(self, position):
        self.current_position = position
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        painter.fillRect(self.rect(), QColor(30, 30, 30))

        if len(self.waveform_data) == 0:
            return

        # Calculate scaling factors
        width = self.width()
        height = self.height()
        samples_per_pixel = max(1, len(self.waveform_data) // width)
        max_amplitude = max(abs(max(self.waveform_data)), abs(min(self.waveform_data)))
        amplitude_scale = height / (2 * max_amplitude)

        # Draw waveform
        painter.setPen(QPen(QColor(0, 255, 0), 1))
        for x in range(width):
            start = x * samples_per_pixel
            end = start + samples_per_pixel
            chunk = self.waveform_data[start:end]
            if len(chunk) > 0:
                min_val = int(min(chunk) * amplitude_scale)
                max_val = int(max(chunk) * amplitude_scale)
                painter.drawLine(x, height//2 - min_val, x, height//2 - max_val)

        # Draw playback position
        if self.duration > 0:
            position_x = int((self.current_position / self.duration) * width)
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            painter.drawLine(position_x, 0, position_x, height)
