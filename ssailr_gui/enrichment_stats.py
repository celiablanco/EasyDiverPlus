import os
import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QFileDialog, QLabel, QLineEdit, QPushButton

class EnrichmentStats(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Enrichment Statistics")
        layout = QVBoxLayout()

        # self.show_find_enrichments()

        # -out
        self.out_file_label = QLabel('File name for out/post-selection file (.txt):')
        self.out_file_edit = QLineEdit()
        self.out_file_button = QPushButton('Browse')
        self.out_file_button.clicked.connect(lambda: self.browse_input("out"))
        layout.addWidget(self.out_file_label)
        layout.addWidget(self.out_file_edit)
        layout.addWidget(self.out_file_button)

        # -in
        self.in_file_label = QLabel('File name for the input file (.txt):')
        self.in_file_edit = QLineEdit()
        self.in_file_button = QPushButton('Browse')
        self.in_file_button.clicked.connect(lambda: self.browse_input("in"))
        layout.addWidget(self.in_file_label)
        layout.addWidget(self.in_file_edit)
        layout.addWidget(self.in_file_button)

        # -neg
        self.neg_file_label = QLabel('File name for negative control file (.txt):')
        self.neg_file_edit = QLineEdit()
        self.neg_file_button = QPushButton('Browse')
        self.neg_file_button.clicked.connect(lambda: self.browse_input("neg"))
        layout.addWidget(self.neg_file_label)
        layout.addWidget(self.neg_file_edit)
        layout.addWidget(self.neg_file_button)

        # -res
        self.res_file_label = QLabel('File name for results file (.txt):')
        self.res_file_edit = QLineEdit()
        self.res_file_button = QPushButton('Browse')
        self.res_file_button.clicked.connect(lambda: self.browse_input("res"))
        layout.addWidget(self.res_file_label)
        layout.addWidget(self.res_file_edit)
        layout.addWidget(self.res_file_button)

        # Calculate
        calculate_button = QPushButton("Calculate", self)
        calculate_button.clicked.connect(self.calculate)
        layout.addWidget(calculate_button)

        self.setLayout(layout)

    def show_find_enrichments(self):
        calculate_enrichment = QMessageBox.question(self, "Find Enrichments", "Calculate enrichment statistics for amino acid counts? (Yes - AA, No - Nucleotide)", QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
        
        if calculate_enrichment == QMessageBox.Yes:
            self.show_output_directory_dialog("AA")
        else:
            self.show_output_directory_dialog("Nucleotides")
               
    def show_output_directory_dialog(self, type):
        if type == "AA":
            pass
        else:
            pass
            
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if output_dir:
            print(output_dir)
            subprocess.run(["python3", self.run_script])

        self.close()

    def browse_input(self, btn_edit_type):
        # Open file dialog to select input file
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Select Input File')
        if file_path:
            if btn_edit_type == "out":
                self.out_file_edit.setText(file_path)
            elif btn_edit_type == "in":
                self.in_file_edit.setText(file_path)
            elif btn_edit_type == "neg":
                self.neg_file_edit.setText(file_path)
            else:
                self.res_file_edit.setText(file_path)
        
    def calculate(self):
        run_script = "modified_counts.py "
        print(os.listdir())
        if not self.out_file_edit.text():
            QMessageBox.critical(self, "Error", "Please enter the required input.")
            return
        else:
            run_script += f"-out {self.out_file_edit.text()} "

        if self.in_file_edit.text():
            run_script += f"-in {self.in_file_edit.text} "

        if self.neg_file_edit.text():
            run_script += f"-neg {self.neg_file_edit.text} "

        if self.res_file_edit.text():
            run_script += f"-res {self.res_file_edit.text}"

        res = subprocess.run(run_script.split(" "))

        if res.returncode == 0:
            self.close()
            