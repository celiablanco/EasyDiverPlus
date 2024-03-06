import os
import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QFileDialog, QPushButton, QMessageBox

class EasyDiver(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Easy Diver")
        layout = QVBoxLayout()

        # Required parameters
        required_label = QLabel("REQUIRED")
        layout.addWidget(required_label)

        # Option -i
        self.input_label = QLabel('Input Directory Filepath:')
        self.input_dir_edit = QLineEdit()
        self.input_button = QPushButton('Browse')
        self.input_button.clicked.connect(self.browse_input)
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_dir_edit)
        layout.addWidget(self.input_button)

        # Optional parameters
        optional_label = QLabel("OPTIONAL")
        layout.addWidget(optional_label)

        # Option -o
        self.output_dir_label = QLabel('Output Directory Filepath:')
        self.output_dir_edit = QLineEdit()
        layout.addWidget(self.output_dir_label)
        layout.addWidget(self.output_dir_edit)

        # Option -p
        self.forward_primer_label = QLabel('Forward Primer Sequence Extraction:')
        self.forward_primer_edit = QLineEdit()
        layout.addWidget(self.forward_primer_label)
        layout.addWidget(self.forward_primer_edit)

        # Option -q
        self.reverse_primer_label = QLabel('Reverse Primer Sequence Extraction:')
        self.reverse_primer_edit = QLineEdit()
        layout.addWidget(self.reverse_primer_label)
        layout.addWidget(self.reverse_primer_edit)

        # Option -a
        self.translate_check = QCheckBox('Translate to Amino Acids:')
        layout.addWidget(self.translate_check)

        # Option -r
        self.retain_check = QCheckBox('Retain Individual Lane Outputs:')
        layout.addWidget(self.retain_check)

        # Option -T
        self.threads_label = QLabel('Number of Threads:')
        self.threads_edit = QLineEdit()
        layout.addWidget(self.threads_label)
        layout.addWidget(self.threads_edit)

        # Option -e
        self.extra_flags_label = QLabel('Extra Flags for PANDASeq (use quotes, e.g. \"-L 50\"):')
        self.extra_flags_edit = QLineEdit()
        layout.addWidget(self.extra_flags_label)
        layout.addWidget(self.extra_flags_edit)

        # Submit
        submit_button = QPushButton("Submit", self)
        submit_button.clicked.connect(self.submit)
        layout.addWidget(submit_button)

        self.setLayout(layout)
    
    def browse_input(self):
        # Open file dialog to select input file
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Select Input File')
        if file_path:
            # relative_path = os.path.relpath(file_path, os.getcwd())
            self.input_dir_edit.setText(file_path)

    def submit(self):
        run_script = "bash easydiver.sh "
        print(os.listdir())
        if not self.input_dir_edit.text():
            QMessageBox.critical(self, "Error", "Please enter the required input.")
            return
        else:
            run_script += f"-i {self.input_dir_edit.text()} "
        
        if self.output_dir_edit.text():
            run_script += f"-o {self.output_dir_edit.text()} "

        if self.forward_primer_edit.text():
            run_script += f"-p {self.forward_primer_edit.text()} "

        if self.reverse_primer_edit.text():
            run_script += f"-q {self.reverse_primer_edit.text()} "

        if self.threads_edit.text():
            run_script += f"-T {self.threads_edit.text()} "

        if self.translate_check:
            run_script += "-a "

        if self.retain_check:
            run_script += "-r "

        if self.extra_flags_edit.text():
            run_script += f"-e \"{self.extra_flags_edit.text()}\""

        res = subprocess.run(run_script.split(" "))

        if res.returncode == 0:
            self.close()