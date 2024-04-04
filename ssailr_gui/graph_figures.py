import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog, QProgressBar, QMessageBox, QLineEdit
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
        self.dropdown.currentIndexChanged.connect(self.update_label_text)
        layout.addWidget(self.dropdown)

        # -dir
        self.graph_dir_label = QLabel('Enter EasyDIVER output directory filepath:')
        self.graph_dir_edit = ClickableDirectoryEdit()
        self.graph_dir_edit.clicked.connect(self.browse_input)
        layout.addWidget(self.graph_dir_label)
        layout.addWidget(self.graph_dir_edit)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

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

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_selected_option(self):
        index = self.dropdown.currentIndex()
        selected_option = self.dropdown.itemText(index)
        return selected_option
    
    def update_label_text(self, index):
        selected_option = self.dropdown.itemText(index)
        if selected_option == "Histogram":
            self.graph_dir_label.setText('Enter EasyDIVER output directory filepath:')
        elif selected_option == "Enrichment Scatterplot":
            self.graph_dir_label.setText('Enter Enrichment result .txt filepath:')
        elif selected_option == "AA Count Line Graph":
            self.graph_dir_label.setText('Enter EasyDIVER output directory filepath:')
        elif selected_option == "Txt to Excel":
            self.graph_dir_label.setText('Enter Enrichment result .txt filepath:')
    
    def browse_input(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if directory:
            self.graph_dir_edit.setText(directory)

    def submit(self):
        run_script = f"python3 graphs.py {self.graph_dir_edit.text()}"
        selected_option = self.get_selected_option()

        if selected_option == "Histogram":
            run_script += " 2"

        if selected_option == "Enrichment Scatterplot":
            run_script += " 1"

        if selected_option == "AA Count Line Graph":
            run_script += " 3"

        if selected_option == "Txt to Excel":
            run_script = f"python3 txt_to_xslx.py {self.graph_dir_edit.text()}"

        print(run_script)
        self.progress_bar.setValue(0)

        # Execute the script
        try:
            progress = 0
            res = subprocess.Popen(run_script.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            
            while True:
                output = res.stdout.readline()
                print(output)

                if res.poll() is not None:
                    break

                print(f"Progress: {progress}")
                self.progress_bar.setValue(progress)
                progress += 1

            if res.returncode == 0:
                self.progress_bar.setValue(100)
                QMessageBox.information(self, "Success", "Task completed successfully.")
                self.close()
            else:
                error_message = res.stderr.read()
                QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")