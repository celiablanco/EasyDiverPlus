import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QFileDialog, QPushButton, QRadioButton, QGroupBox, QProgressBar
from directory_edit import ClickableDirectoryEdit

class EnrichmentStats(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Enrichment Statistics")
        layout = QVBoxLayout()

        # Required parameters
        required_label = QLabel("REQUIRED")
        layout.addWidget(required_label)

        # -dir
        self.easy_diver_dir_label = QLabel('Enter the filepath for the EasyDIVER output directory:')
        self.easy_diver_dir_edit = ClickableDirectoryEdit()
        self.easy_diver_dir_edit.clicked.connect(self.browse_input)
        layout.addWidget(self.easy_diver_dir_label)
        layout.addWidget(self.easy_diver_dir_edit)

        # Enrichment Type
        group_box = QGroupBox("Enrichment Type")

        # - AA and Nucleotide
        self.radio_aa = QRadioButton("AA")
        self.radio_nucleotide = QRadioButton("Nucleotide")
        self.radio_aa.setChecked(True)

        # Add radio buttons to a layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.radio_aa)
        vbox.addWidget(self.radio_nucleotide)
        group_box.setLayout(vbox)
        layout.addWidget(group_box)

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
        calculate_button.clicked.connect(self.calculate)
        button_layout.addWidget(calculate_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def browse_input(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if directory:
            self.easy_diver_dir_edit.setText(directory)
        
    def calculate(self):
        run_script = "python3 modified_counts.py "
        if not self.easy_diver_dir_edit.text():
            QMessageBox.critical(self, "Error", "Please enter the required input.")
            return
        else:
            run_script += f"-dir {self.easy_diver_dir_edit.text()}"
        
        if self.radio_aa.isChecked():
            run_script += f" -count counts.aa"
        else:
            run_script += f" -count counts"
        
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