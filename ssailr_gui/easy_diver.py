import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QMessageBox, QLabel

class EasyDiver(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        label = QLabel("Easy Diver")
        layout.addWidget(label)
        
        self.setLayout(layout)