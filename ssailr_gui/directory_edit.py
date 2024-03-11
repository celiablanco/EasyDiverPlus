import os
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QLineEdit

class ClickableDirectoryEdit(QLineEdit):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def setText(self, text):
        if os.path.isdir(text):
            super().setText(text)
        else:
            raise ValueError("Invalid directory path")