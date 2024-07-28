import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QFileDialog
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QPixmap, QCloseEvent
from PyQt5.QtCore import Qt, QEvent # type: ignore # pylint: disable=import-error
from directory_edit import ClickableDirectoryEdit

class Graphs_Window(QWidget):
    def __init__(self, parent = None, rounds_path = None):
        super().__init__(parent)
        self.rounds_path = rounds_path
        self.inputs = {}
        self.worker = None
        self.graph_tasks = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        if self.rounds_path is None:
            self.input_layout = QHBoxLayout()
            self.input_label = QLabel("Input Path for Parent Directory:")
            self.input_dir_edit = ClickableDirectoryEdit()
            self.input_dir_edit.clicked.connect(self.browse_input)
            self.input_tooltip_icon = QLabel()
            self.input_tooltip_icon.setPixmap(
                QPixmap("ssailr_gui/assets/question_icon.png").scaled(20, 20)
            )
            self.input_tooltip_icon.setToolTip(
                "Select the directory containing the modified_counts folder(s)."
            )
            self.input_layout.addWidget(self.input_label)
            self.input_layout.addWidget(self.input_dir_edit)
            self.input_layout.addWidget(self.input_tooltip_icon)
            layout.addLayout(self.input_layout)
        # Select Round
        self.dna_or_aa_layout = QHBoxLayout()
        self.dna_or_aa_label = QLabel("Select Data Type:")
        self.dna_or_aa_combo = QComboBox()
        self.dna_or_aa_combo.addItem('DNA')
        self.dna_or_aa_combo.addItem('AA')
        self.dna_or_aa_combo.setCurrentIndex(-1)
        self.dna_or_aa_layout.addWidget(self.dna_or_aa_label)
        self.dna_or_aa_layout.addWidget(self.dna_or_aa_combo)
        self.dna_or_aa_combo.currentIndexChanged.connect(self.populate_rounds)
        layout.addLayout(self.dna_or_aa_layout)

        # Select Round
        round_layout = QHBoxLayout()
        round_label = QLabel("Select Round:")
        self.round_combo = QComboBox()
        self.populate_rounds()
        round_layout.addWidget(round_label)
        round_layout.addWidget(self.round_combo)
        layout.addLayout(round_layout)


        # Define input configurations
        input_configurations = [
            ("Count_out cutoff threshold:", 0, False),
            ("Freq_out cutoff threshold:", 0.0000000, True),
            ("Count_in cutoff threshold:", 0, False),
            ("Freq_in cutoff threshold:", 0.0000000, True),
            ("Count_neg cutoff threshold:", 0, False),
            ("Freq_neg cutoff threshold:", 0.0000000, True),
            ("Enr_out cutoff threshold:", 0, False),
            ("Enr_neg cutoff threshold:", 0, False)
        ]

        for label_text, default_value, is_float in input_configurations:
            input_field = self.create_input_field(label_text, default_value, layout, is_float)
            self.inputs[label_text] = input_field

        self.buttons_box = QHBoxLayout()
        # Generate Graphs Button
        self.generate_button = QPushButton("Generate Graphs")
        self.generate_button.clicked.connect(self.generate_graphs)
        self.buttons_box.addWidget(self.generate_button)

        # Generate Graphs Button
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        self.buttons_box.addWidget(self.exit_button)
        layout.addLayout(self.buttons_box)

        self.setLayout(layout)
        self.setWindowTitle("Graph Generator")
        self.center_window()
        self.setWindowFlags(Qt.Window)
        self.show()
    
    def populate_rounds(self):
        # Assuming the directory containing rounds is pre-defined in the code
        self.round_combo.clear()
        mod_counts = 'modified_counts'
        if self.dna_or_aa_combo.currentText() == 'AA':
            mod_counts = mod_counts+'.aa'
        if self.rounds_path is not None:
            rounds_directory = f"{self.rounds_path}/{mod_counts}"
            rounds = sorted([f for f in os.listdir(rounds_directory) if f.startswith('round_')])
            for round_name in rounds:
                self.round_combo.addItem(round_name.split('_')[1])
    
    def create_input_field(self, label_text, default_value, layout, is_float=False):
        input_layout = QHBoxLayout()
        label = QLabel(label_text)
        input_field = QLineEdit()
        input_field.setText(str(default_value))
        if is_float:
            input_field.setValidator(QDoubleValidator(0.0, 1.0, 7))
        else:
            input_field.setValidator(QIntValidator(0, 10000))
        input_layout.addWidget(label)
        input_layout.addWidget(input_field)
        layout.addLayout(input_layout)
        return input_field

    def generate_graphs(self):
        # Implement the graph generation logic here
        mod_counts = 'modified_counts'
        if self.dna_or_aa_combo.currentText() == 'AA':
            mod_counts = mod_counts+'.aa'
        input_values = {label: field.text() for label, field in self.inputs.items()}
        run_script = f'python "ssailr_gui/graphs_generator.py" --round_file {self.rounds_path}/{mod_counts}/round_{self.round_combo.currentText()}_enrichment_analysis.csv '
        for input_val in input_values:
            arg_label = input_val.lower().replace(' cutoff threshold:','')
            arg_value = input_values.get(input_val)
            run_script +=f'--{arg_label} {arg_value} '

        try:
            result = subprocess.run(run_script, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode('utf-8')
            error = result.stderr.decode('utf-8')
            
            if output:
                print("Output:", output)
            if error:
                print("Error:", error)
            
            QMessageBox.information(self, "Graphs Generated", "The graphs have been generated successfully.")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8') if e.stderr else str(e)
            print("An error occurred:", error_msg)
            QMessageBox.critical(self, "Error", f"An error occurred:\n{error_msg}")

    def browse_input(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        mod_counts_exists = False
        if directory:
            for f in os.listdir(directory):
                if f == 'modified_counts':
                    mod_counts_exists = True
                    self.input_dir_edit.setText(directory)
                    self.rounds_path = directory

        if mod_counts_exists is False:
            QMessageBox.critical(
                self,
                "Error",
                "Please choose the parent directory containing the 'modified_counts' folder.",
            )

    def center_window(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def closeEvent(self, event: QCloseEvent) -> None: # pylint: disable=invalid-name
        """
        Handle the event when the application window is closed,
        ensuring the interaction button is disabled in the main window
        and the submit button is enabled in the main window, if and only if
        the saved choices was successful, meaning the sorting is completed.
        """
        # Ensure the parent exists and the button exists before trying to disable it
        if (self.parent() is not None):
            QMessageBox.information(
                self, "Success", "All tasks completed successfully."
            )
            self.parent().close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    rounds_path = None
    try:
        rounds_path = sys.argv[1]
    except Exception as e:
        print("no input given")
    window = Graphs_Window(parent = None, rounds_path = rounds_path)
    sys.exit(app.exec_())
