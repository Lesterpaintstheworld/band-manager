from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath
import random

class WaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.waveform_data = []
        self.current_position = 0
        self.duration = 0
        self.setMinimumHeight(100)

        # Generate initial random waveform data
        self.generate_random_waveform()

        # Timer to update waveform
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_waveform)
        self.update_timer.start(50)  # Update every 50ms

    def generate_random_waveform(self):
        self.waveform_data = [random.randint(10, 90) for _ in range(100)]

    def update_waveform(self):
        # Shift waveform data and add new random value
        self.waveform_data = self.waveform_data[1:] + [random.randint(10, 90)]
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

        if not self.waveform_data:
            return

        # Calculate width of each bar
        width = self.width() / len(self.waveform_data)
        mid_height = self.height() / 2

        # Draw waveform
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        path = QPainterPath()
        path.moveTo(0, mid_height)
        for i, value in enumerate(self.waveform_data):
            x = i * width
            y = mid_height - value
            path.lineTo(x, y)
        for i in range(len(self.waveform_data) - 1, -1, -1):
            x = i * width
            y = mid_height + self.waveform_data[i]
            path.lineTo(x, y)
        path.closeSubpath()
        painter.fillPath(path, QColor(0, 255, 0, 100))
        painter.drawPath(path)

        # Draw playback position
        if self.duration > 0:
            position_x = int((self.current_position / self.duration) * self.width())
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            painter.drawLine(position_x, 0, position_x, self.height())
