from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt5.QtCore import Qt
from concept import ConceptTab
from lyrics import LyricsTab
from composition import CompositionTab
from production import ProductionTab
from visual_design import VisualDesignTab
from concert import ConcertTab

class MainInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Synthetic Band Manager')
        self.showFullScreen()

        layout = QVBoxLayout()
        self.setLayout(layout)

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
