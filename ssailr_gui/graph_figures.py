from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog
from directory_edit import ClickableDirectoryEdit

class GraphFigures(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Graph Figures")
        layout = QVBoxLayout()

        # Required parameters
        required_label = QLabel("REQUIRED")
        layout.addWidget(required_label)

        # Dropdown menu
        self.dropdown = QComboBox()
        self.dropdown.addItem("Histogram")
        self.dropdown.addItem("Enrichment Scatterplot")
        self.dropdown.addItem("AA Count Line Graph")
        self.dropdown.addItem("Txt to Excel")
        self.dropdown.setCurrentIndex(0)
        layout.addWidget(self.dropdown)

        # -dir
        self.easy_diver_dir_label = QLabel('Enter the filepath for the EasyDIVER output directory:')
        self.easy_diver_dir_edit = ClickableDirectoryEdit()
        self.easy_diver_dir_edit.clicked.connect(self.browse_input)
        layout.addWidget(self.easy_diver_dir_label)
        layout.addWidget(self.easy_diver_dir_edit)

        # Horizontal layout
        button_layout = QHBoxLayout()

        # Cancel
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)

        # Calculate
        calculate_button = QPushButton("Calculate", self)
        calculate_button.clicked.connect(self.submit)
        button_layout.addWidget(calculate_button)

        layout.addWidget(button_layout)
        self.setLayout(layout)

    def get_selected_option(self):
        index = self.dropdown.currentIndex()
        selected_option = self.dropdown.itemText(index)
        return selected_option
    
    def browse_input(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if directory:
            self.easy_diver_dir_edit.setText(directory)
    
    def submit(self):
        run_script = "python3 graphs.py"
        selected_option = self.get_selected_option()

        print("Selected option:", selected_option)

        if selected_option == "Histogram":
            run_script += " 2"

        if selected_option == "Enrichment Scatterplot":
            run_script += " 1"

        if selected_option == "AA Count Line Graph":
            run_script += " 3"

        if selected_option == "Txt to Excel":
            run_script += " "