import os
import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QFileDialog, QPushButton
from directory_edit import ClickableDirectoryEdit

class EnrichmentStats(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Enrichment Statistics")
        layout = QVBoxLayout()

        self.enrichment_type = self.show_enrichment_type()

        # Required parameters
        required_label = QLabel("REQUIRED")
        layout.addWidget(required_label)

        # -dir
        self.easy_diver_dir_label = QLabel('Enter the filepath for the EasyDIVER output directory:')
        self.easy_diver_dir_edit = ClickableDirectoryEdit()
        self.easy_diver_dir_edit.clicked.connect(self.browse_input)
        layout.addWidget(self.easy_diver_dir_label)
        layout.addWidget(self.easy_diver_dir_edit)

        # -out
        self.out_file_label = QLabel('File name for out/post-selection file (.txt):')
        self.out_file_edit = QLineEdit()
        layout.addWidget(self.out_file_label)
        layout.addWidget(self.out_file_edit)

        # Optional parameters
        optional_label = QLabel("OPTIONAL")
        layout.addWidget(optional_label)

        # -in
        self.in_file_label = QLabel('File name for the input file (.txt):')
        self.in_file_edit = QLineEdit()
        layout.addWidget(self.in_file_label)
        layout.addWidget(self.in_file_edit)

        # -neg
        self.neg_file_label = QLabel('File name for negative control file (.txt):')
        self.neg_file_edit = QLineEdit()
        layout.addWidget(self.neg_file_label)
        layout.addWidget(self.neg_file_edit)

        # -res
        self.res_file_label = QLabel('File name for results file (.txt):')
        self.res_file_edit = QLineEdit()
        layout.addWidget(self.res_file_label)
        layout.addWidget(self.res_file_edit)

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

    def show_enrichment_type(self):
        calculate_enrichment = QMessageBox.question(self, "Find Enrichments", "Calculate enrichment statistics for amino acid counts? (Yes - AA, No - Nucleotide)", QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
        
        if calculate_enrichment == QMessageBox.Yes:
            counts_type = "counts.aa"
        else:
            counts_type = "counts"

        return counts_type
    
    def browse_input(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if directory:
            self.easy_diver_dir_edit.setText(directory)
        
    def calculate(self):
        run_script = "python3 modified_counts.py "
        if not self.out_file_edit.text():
            QMessageBox.critical(self, "Error", "Please enter the required input.")
            return
        else:
            run_script += f"-out {self.out_file_edit.text()} "

        if self.easy_diver_dir_edit.text():
            run_script += f"-dir {self.easy_diver_dir_edit.text()}"

        if self.in_file_edit.text():
            run_script += f"-in {self.in_file_edit.text()} "

        if self.neg_file_edit.text():
            run_script += f"-neg {self.neg_file_edit.text()} "

        if self.res_file_edit.text():
            run_script += f"-res {self.res_file_edit.text()}"

        print(run_script)

        res = subprocess.run(run_script.split(" "))

        if res.returncode == 0:
            self.close()