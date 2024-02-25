import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog
from PyQt5.QtGui import QFont

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Main Menu")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        options = ["Run All", "Use EasyDIVER", "Calculate Enrichment Statistics", "Figures and Misc.", "Help", "Quit"]
        for option in options:
            button = QPushButton(option, self)
            button.clicked.connect(self.exit_application)
            layout.addWidget(button)

        self.setLayout(layout)
        self.show()

    def exit_application(self):
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainMenu()
    sys.exit(app.exec_())