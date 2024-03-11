import os
import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QMessageBox, QFileDialog, QPushButton

class EnrichmentStats(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Enrichment Statistics")
        layout = QVBoxLayout()

        self.enichment_type = self.show_enrichment_type()

        # -out
        self.out_file_label = QLabel('File name for out/post-selection file (.txt):')
        self.out_file_edit = QLineEdit()
        layout.addWidget(self.out_file_label)
        layout.addWidget(self.out_file_edit)

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

        # Calculate
        calculate_button = QPushButton("Calculate", self)
        calculate_button.clicked.connect(self.calculate)
        layout.addWidget(calculate_button)

        self.setLayout(layout)

    def show_enrichment_type(self):
        calculate_enrichment = QMessageBox.question(self, "Find Enrichments", "Calculate enrichment statistics for amino acid counts? (Yes - AA, No - Nucleotide)", QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
        
        if calculate_enrichment == QMessageBox.Yes:
            enrichment_type = "AA"
        else:
            enrichment_type = "Nucleotides"

        return enrichment_type
               
    def select_output_directory(self):
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if output_dir:
            print(output_dir)
        
    def calculate(self):
        run_script = "python3 modified_counts.py "
        if not self.out_file_edit.text():
            QMessageBox.critical(self, "Error", "Please enter the required input.")
            return
        else:
            run_script += f"-out {self.out_file_edit.text()} "

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