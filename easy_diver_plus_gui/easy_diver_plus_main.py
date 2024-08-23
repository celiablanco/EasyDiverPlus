#!/usr/bin/python
import sys
import os
import atexit
import signal
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QFileDialog,
    QPushButton,
    QMessageBox,
    QTextEdit,
    QSpinBox,
    QSplitter
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from graph_interface import Graphs_Window
from easy_diver import EasyDiver

if os.name == 'nt':
    import msvcrt
else:
    import fcntl

lock_file = None

def release_lockfile(lockfile):
    global lock_file
    if lock_file:
        if os.name == 'nt':
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()
        os.remove(lockfile)

def check_single_instance(lockfile):
    global lock_file
    lock_file = open(lockfile, 'w')
    try:
        if os.name == 'nt':
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("Another instance is already running.")
        sys.exit(1)

    # Set up signal handling to release the lockfile on termination
    signal.signal(signal.SIGINT, lambda signum, frame: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))

    # Register the release_lockfile function to be called on exit
    atexit.register(release_lockfile, lockfile)

def path_constructor(path: str, parent_path: str) -> str:

    # Determine if we are running in a bundled mode
    if hasattr(sys, '_MEIPASS'):
        # We are running in a bundled mode, use sys._MEIPASS
        base_path = sys._MEIPASS
    else:
        # We are running in normal mode, use the script directory
        base_path = os.path.abspath(".")

    # Construct the path to the image file
    adjusted_path = os.path.join(base_path, parent_path, path)
    return adjusted_path

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.graphi = None
        self.easy_diver_app = None

    def init_ui(self):
        self.setWindowTitle("Easy Diver+")
        layout = QVBoxLayout()
        
        # Create a splitter
        splitter = QSplitter(Qt.Vertical)

        # add logo
        self.image_widget = QWidget()
        self.image_layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_pixmap = QPixmap(path_constructor("logo.png","easy_diver_plus_gui/assets/")).scaledToWidth(15000)
        self.image_label.setPixmap(self.image_pixmap)
        self.image_layout.addWidget(self.image_label)
        self.image_widget.setLayout(self.image_layout)

        splitter.addWidget(self.image_widget)
        
        # Horizontal layout
        self.button_widget = QWidget()
        button_layout = QHBoxLayout()
        # Help
        self.help_button = QPushButton("Help", self)
        self.help_button.setToolTip(
            "Click to access additional help information."
        )
        self.help_button.clicked.connect(self.display_help_message)

        # Cancel
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setToolTip("Click to cancel and close the application.")
        self.cancel_button.clicked.connect(self.close)

        # Easy Diver
        self.easy_diver_button = QPushButton("Easy Diver+", self)
        self.easy_diver_button.setToolTip(
            "Click to start the Easy Diver+ interactive application."
        )
        self.easy_diver_button.clicked.connect(self.easy_diver)

        # Graphing Interface
        self.graph_button = QPushButton("Graph Generator", self)
        self.graph_button.setToolTip(
            "Click to start the Graph Generator interactive application."
        )
        self.graph_button.clicked.connect(self.grapher)
        
        button_layout.addWidget(self.easy_diver_button)
        button_layout.addWidget(self.graph_button)
        button_layout.addWidget(self.help_button)
        button_layout.addWidget(self.cancel_button)
        self.button_widget.setLayout(button_layout)
        splitter.addWidget(self.button_widget)
        layout.addWidget(splitter)
        self.setLayout(layout)
        self.setMinimumSize(600, 300)
        self.setMaximumSize(1000, 1600)  # Adjust as needed
        self.resize(800,300)
        self.setWindowFlags(Qt.Window)
        self.center_window()
        self.show()

    def update_image_size(self):
        self.image_label.setPixmap(
            self.image_pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio)
        )

    def center_window(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def resizeEvent(self, event):
        self.update_image_size()
        super().resizeEvent(event)
    
    def grapher(self):
        self.graphi = Graphs_Window(self)
        self.graphi.show()
    def easy_diver(self):
        self.easy_diver_app = EasyDiver(self)
        self.easy_diver_app.show()

    def display_help_message(self):
        help_text = """
        EasyDiver+ is a pipeline to processes and analyzes raw sequencing data files from consecutive rounds of selection/evolution, providing:
        - Read count files
        - Sequence length distribution
        - Enrichment metrics across consecutive rounds of selection
        - Visualizations

        Graph Generator is an application to process the enrichment analysis outputs of Easy Diver+ into plotly charts in a customizable manner.
        The user may edit the parameters and re-generate the graphs as many times as needed. Each new generation of plots will open in a new tab in
        the user's default browser. Once satisfied, the user may save the graphs via the web view display which opens.
        This can be run independently of Easy Diver+, allowing the user to go through the process of identifying the appropriate graph and customization for their needs.
        """

        QMessageBox.information(self, "Help", help_text)

if __name__ == "__main__":
    try:
        lockfile = 'easy_diver2.lock'
        check_single_instance(lockfile)
        app = QApplication(sys.argv)
        window = MainApp()
        sys.exit(app.exec_())
    finally:
        release_lockfile(lockfile)