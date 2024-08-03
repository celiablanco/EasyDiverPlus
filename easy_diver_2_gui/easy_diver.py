#!/usr/bin/python
import subprocess
import sys
import os
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
from PyQt5.QtGui import QPixmap, QCloseEvent
from PyQt5.QtCore import Qt

from directory_edit import ClickableDirectoryEdit
from file_sorter import SortingApp
from graph_interface import Graphs_Window
from modified_counts import find_enrichments as mod_counts_main

def path_constructor(path: str, parent_path: str) -> str:

    # Determine if we are running in a bundled mode
    if hasattr(sys, '_MEIPASS'):
        # We are running in a bundled mode, use sys._MEIPASS
        base_path = sys._MEIPASS
    else:
        # We are running in normal mode, use the script directory
        base_path = os.path.abspath(".")

    # Construct the path to the image file
    if parent_path == '.':
        adjusted_path = os.path.join(base_path, path)
    else:
        adjusted_path = os.path.join(base_path, parent_path, path)
    return adjusted_path

class QTextEditStream:
    def __init__(self, text_edit: QTextEdit):
        self.text_edit = text_edit

    def write(self, message):
        self.text_edit.append(message)

    def flush(self):
        pass  # Not needed for this implementation

class EasyDiver(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.init_ui()
        self.graphi = None
        self.dash_thread = None
        self.output_dir = ""

    def init_ui(self):
        if (self.parent() is not None):
            self.parent().close()
        self.setWindowTitle("Easy Diver 2.0")
        layout = QVBoxLayout()

        # Create a splitter
        splitter = QSplitter(Qt.Vertical)

        # add logo
        self.image_widget = QWidget()
        self.image_layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_pixmap = QPixmap(path_constructor("logo.png","easy_diver_2_gui/assets/")).scaledToWidth(15000)
        self.image_label.setPixmap(self.image_pixmap)
        self.image_layout.addWidget(self.image_label)
        self.image_widget.setLayout(self.image_layout)

        splitter.addWidget(self.image_widget)

        # Required parameters
        self.required_widget = QWidget()
        self.required_layout = QVBoxLayout()
        self.required_label = QLabel("REQUIRED")
        self.required_layout.addWidget(self.required_label)
        question_path = path_constructor("question_icon.png","easy_diver_2_gui/assets/")
        # Option -i
        self.input_label = QLabel("Input Directory Path:")
        self.input_dir_edit = ClickableDirectoryEdit()
        self.input_dir_edit.clicked.connect(self.browse_input)
        input_tooltip_icon = QLabel()
        input_tooltip_icon.setPixmap(
            QPixmap(question_path).scaled(20, 20)
        )
        input_tooltip_icon.setToolTip(
            "Select the directory containing the input files."
        )

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_dir_edit)
        input_layout.addWidget(input_tooltip_icon)
        self.required_layout.addLayout(input_layout)

        self.required_widget.setLayout(self.required_layout)
        splitter.addWidget(self.required_widget)

        # Optional parameters

        self.optional_widget = QWidget()
        self.optional_layout = QVBoxLayout()

        optional_label = QLabel("OPTIONAL")
        self.optional_layout.addWidget(optional_label)

        # Option -o
        self.output_label = QLabel("Output Directory Path:")
        self.output_dir_edit = QLineEdit()
        output_tooltip_icon = QLabel()
        output_tooltip_icon.setPixmap(
            QPixmap(question_path).scaled(20, 20)
        )
        output_tooltip_icon.setToolTip(
            "Specify the directory to save output files. If not provided, it defaults to the input directory with '/pipeline.output' appended."
        )

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(output_tooltip_icon)
        self.optional_layout.addLayout(output_layout)

        # Option -p
        self.forward_primer_label = QLabel("Forward Primer Sequence Extraction:")
        self.forward_primer_edit = QLineEdit()
        forward_primer_tooltip_icon = QLabel()
        forward_primer_tooltip_icon.setPixmap(
            QPixmap(question_path).scaled(20, 20)
        )
        forward_primer_tooltip_icon.setToolTip(
            "Enter the forward primer sequence for extraction."
        )

        forward_primer_layout = QHBoxLayout()
        forward_primer_layout.addWidget(self.forward_primer_label)
        forward_primer_layout.addWidget(self.forward_primer_edit)
        forward_primer_layout.addWidget(forward_primer_tooltip_icon)
        self.optional_layout.addLayout(forward_primer_layout)

        # Option -q
        self.reverse_primer_label = QLabel("Reverse Primer Sequence Extraction:")
        self.reverse_primer_edit = QLineEdit()
        reverse_primer_tooltip_icon = QLabel()
        reverse_primer_tooltip_icon.setPixmap(
            QPixmap(question_path).scaled(20, 20)
        )
        reverse_primer_tooltip_icon.setToolTip(
            "Enter the reverse primer sequence for extraction."
        )

        reverse_primer_layout = QHBoxLayout()
        reverse_primer_layout.addWidget(self.reverse_primer_label)
        reverse_primer_layout.addWidget(self.reverse_primer_edit)
        reverse_primer_layout.addWidget(reverse_primer_tooltip_icon)
        self.optional_layout.addLayout(reverse_primer_layout)

        # Option -e
        self.extra_flags_label = QLabel(
            'Extra Flags for PANDASeq (use quotes, e.g. "-L 50"):'
        )
        self.extra_flags_edit = QLineEdit()
        extra_flags_tooltip_icon = QLabel()
        extra_flags_tooltip_icon.setPixmap(
            QPixmap(question_path).scaled(20, 20)
        )
        extra_flags_tooltip_icon.setToolTip(
            'Enter any extra flags for PANDASeq, enclosed in quotes (e.g., "-L 50").'
        )

        extra_flags_layout = QHBoxLayout()
        extra_flags_layout.addWidget(self.extra_flags_label)
        extra_flags_layout.addWidget(self.extra_flags_edit)
        extra_flags_layout.addWidget(extra_flags_tooltip_icon)
        self.optional_layout.addLayout(extra_flags_layout)
        
        # Option -a
        self.skip_processing = QCheckBox("Skip Processing (enrichment analysis only)")
        skip_processing_icon = QLabel()
        skip_processing_icon.setPixmap(
            QPixmap(question_path).scaled(20, 20)
        )
        skip_processing_icon.setToolTip(
            "Check this box to skip processing, use this option only if you have already processed the data and want to only run enrichment analysis."
        )

        skip_processing_layout = QHBoxLayout()
        skip_processing_layout.addWidget(self.skip_processing)
        skip_processing_layout.addStretch()
        skip_processing_layout.addWidget(skip_processing_icon)
        self.optional_layout.addLayout(skip_processing_layout)

        # Option -a
        self.translate_check = QCheckBox("Translate to Amino Acids")
        translate_tooltip_icon = QLabel()
        translate_tooltip_icon.setPixmap(
            QPixmap(question_path).scaled(20, 20)
        )
        translate_tooltip_icon.setToolTip(
            "Check this box to translate nucleotide sequences to amino acids."
        )

        translate_layout = QHBoxLayout()
        translate_layout.addWidget(self.translate_check)
        translate_layout.addStretch()
        translate_layout.addWidget(translate_tooltip_icon)
        self.optional_layout.addLayout(translate_layout)

        # Option -r
        self.retain_check = QCheckBox("Retain Individual Lane Outputs")
        retain_tooltip_icon = QLabel()
        retain_tooltip_icon.setPixmap(
            QPixmap(question_path).scaled(20, 20)
        )
        retain_tooltip_icon.setToolTip(
            "Check this box to retain outputs for individual lanes."
        )

        retain_layout = QHBoxLayout()
        retain_layout.addWidget(self.retain_check)
        retain_layout.addStretch()
        retain_layout.addWidget(retain_tooltip_icon)
        self.optional_layout.addLayout(retain_layout)

        # Option for enrichment_analysis
        self.run_enrichment_analysis = QCheckBox("Run Enrichment Analysis")
        self.run_enrichment_analysis.stateChanged.connect(self.toggle_precision_option)
        enrichment_analysis_tooltip_icon = QLabel()
        enrichment_analysis_tooltip_icon.setPixmap(
            QPixmap(question_path).scaled(20, 20)
        )
        enrichment_analysis_tooltip_icon.setToolTip(
            "Check this box to run enrichment analysis."
        )

        enrichment_analysis_layout = QHBoxLayout()
        enrichment_analysis_layout.addWidget(self.run_enrichment_analysis)
        enrichment_analysis_layout.addStretch()
        enrichment_analysis_layout.addWidget(enrichment_analysis_tooltip_icon)
        self.optional_layout.addLayout(enrichment_analysis_layout)

        self.enrichment_layout = QVBoxLayout()
        # Additional option for precision
        self.precision_label = QLabel("Output Decimal Precision:")
        self.precision_input = QSpinBox()
        self.precision_input_tooltip_icon = QLabel()
        self.precision_input_tooltip_icon.setPixmap(
            QPixmap(question_path).scaled(20, 20)
        )
        self.precision_input_tooltip_icon.setToolTip(
            "Enter an integer value for the precision of decimal numbers that will be printed in the enrichment output files. Default is 6, max is 10."
        )
        self.precision_input.setRange(0, 10)
        self.precision_input.setValue(6)

        self.precision_layout = QHBoxLayout()
        self.precision_layout.addWidget(self.precision_label)
        self.precision_layout.addWidget(self.precision_input)
        self.precision_layout.addStretch()
        self.precision_layout.addWidget(self.precision_input_tooltip_icon)
        self.enrichment_layout.addLayout(self.precision_layout)

         # Additional button to open the interaction window
        self.interaction_button = QPushButton("REQUIRED: Sort files into rounds and types!")
        self.interaction_button.clicked.connect(self.open_sorting_window)
        self.enrichment_layout.addWidget(self.interaction_button)
        self.optional_layout.addLayout(self.enrichment_layout)
        # Hide the enrichment options initially
        self.toggle_layout(self.enrichment_layout, False)


        # Option for plots generation
        # self.generate_plots = QCheckBox("Generate Plots")
        # generate_plots_tooltip_icon = QLabel()
        # generate_plots_tooltip_icon.setPixmap(
        #     QPixmap(question_path).scaled(20, 20)
        # )
        # generate_plots_tooltip_icon.setToolTip("Check to generate plots from the data.")

        # generate_plots_layout = QHBoxLayout()
        # generate_plots_layout.addWidget(self.generate_plots)
        # generate_plots_layout.addStretch()
        # generate_plots_layout.addWidget(generate_plots_tooltip_icon)
        # self.optional_layout.addLayout(generate_plots_layout)

        self.optional_widget.setLayout(self.optional_layout)
        splitter.addWidget(self.optional_widget)
        self.toggle_layout(self.optional_layout, False)
        layout.addWidget(splitter)
        # Text box to display terminal output
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        # Horizontal layout
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

        # Submit
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.setToolTip(
            "Click to start the process with the specified parameters."
        )
        self.submit_button.clicked.connect(self.submit)
        self.submit_button.setDisabled(True)

        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.help_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setMinimumSize(600, 500)
        self.setMaximumSize(1000, 1600)  # Adjust as needed
        self.resize(800,900)
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

    def toggle_precision_option(self, state):
        if state == Qt.Checked:
            self.precision_label.show()
            self.precision_input.show()
            self.precision_input_tooltip_icon.show()
            if self.input_dir_edit.text() != "":
                self.interaction_button.show()
            self.submit_button.setDisabled(True)
        else:
            self.precision_label.hide()
            self.precision_input.hide()
            self.precision_input_tooltip_icon.hide()
            self.interaction_button.hide()
            self.submit_button.setDisabled(False)

    def open_sorting_window(self):
        sorting_window = SortingApp(self, self.input_dir_edit.text(),self.output_dir_edit.text())
        sorting_window.show()

    def browse_input(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.input_dir_edit.setText(directory)
            self.submit_button.setDisabled(False)
            self.toggle_layout(self.optional_layout, True)
            self.toggle_layout(self.enrichment_layout, False)
            self.run_enrichment_analysis.setChecked(False)

    def submit(self):
        if self.output_dir_edit.text():
            self.output_dir = f"{self.input_dir_edit.text()}/{self.output_dir_edit.text()}"
        else:
            self.output_dir = f"{self.input_dir_edit.text()}/pipeline.output"
        if self.skip_processing.isChecked():
            self.run_enrichment_analysis_steps(self.output_dir, self.precision_input.value())
        else:
            easy_diver_path = path_constructor("easydiver.sh", ".")
            run_script = f"bash {easy_diver_path} "
            if not self.input_dir_edit.text():
                QMessageBox.critical(self, "Error", "Please enter the required input.")
                return
            
            run_script += f"-i {self.input_dir_edit.text()}"

            if self.output_dir_edit.text():
                run_script += f" -o {self.output_dir_edit.text()}"

            if self.forward_primer_edit.text():
                run_script += f" -p {self.forward_primer_edit.text()}"

            if self.reverse_primer_edit.text():
                run_script += f" -q {self.reverse_primer_edit.text()}"

            if self.translate_check.isChecked():
                run_script += " -a"

            if self.retain_check.isChecked():
                run_script += " -r"

            if self.extra_flags_edit.text():
                run_script += f' -e "{self.extra_flags_edit.text()}"'
            # Execute the script
            try:
                res = subprocess.Popen(
                    run_script.split(" "),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                )

                while True:
                    output = res.stdout.readline()
                    if output == "" and res.poll() is not None:
                        break
                    if output:
                        self.output_text.append(output.strip())
                        self.output_text.ensureCursorVisible()
                        QApplication.processEvents()
                        print(output)

                if res.returncode == 0:
                    self.run_enrichment_analysis_steps(self.output_dir, self.precision_input.value())
                else:
                    error_message = res.stderr.read()
                    self.output_text.append(f"Error: {error_message}")
                    self.output_text.ensureCursorVisible()
                    QMessageBox.critical(
                        self, "Error", f"An error occurred: {error_message}"
                    )

            except Exception as e:
                self.output_text.append(f"Error: {str(e)}")
                self.output_text.ensureCursorVisible()
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def run_enrichment_analysis_steps(self, output_dir, precision):
        original_stdout = sys.stdout  # Save a reference to the original standard output

        try:
            # Redirect sys.stdout to the QTextEditStream
            sys.stdout = QTextEditStream(self.output_text)

            if self.run_enrichment_analysis.isChecked():
                mod_counts = mod_counts_main(output_dir, precision)
                if mod_counts is True:
                    self.on_calculate_finish(0, output_dir)
                else:
                    self.on_calculate_finish(1, output_dir)
            else:
                self.on_calculate_finish(0, output_dir)
        finally:
            # Restore the original sys.stdout
            sys.stdout = original_stdout

    def on_calculate_finish(self, returncode, output_dir):
        if returncode == 0:
            print("<===> enrichment_analysis FINISHED <===>")
            print("<===> Graph interface started <===>")
            graphi = Graphs_Window(self, output_dir)
            graphi.show()
        else:
            QMessageBox.critical(
                self,
                "Error",
                "enrichment_analysis calculation failed. Please check the logs for more details.",
            )
        

    def on_graphs_finish(self, returncode):
        if returncode == 0:
            QMessageBox.information(
                self, "Success", "All tasks completed successfully."
            )
            self.close()
            
        else:
            QMessageBox.critical(
                self,
                "Error",
                "An error occurred during graph generation. Please check the logs for more details.",
            )
    def toggle_layout(self, layout, visible):
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if isinstance(item, QHBoxLayout) or isinstance(item, QVBoxLayout):
                self.toggle_layout(item, visible)
            elif item.widget():
                item.widget().setVisible(visible)
    
    def display_help_message(self):
        help_text = """
        EasyDIVER 2.0 is a pipeline to processes and analyzes raw sequencing data files from consecutive rounds of selection/evolution, providing:
        - Read count files
        - Sequence length distribution
        - Enrichment metrics across consecutive rounds of selection
        - Visualizations

        Version 2.0

        REQUIRED:
        - Input directory filepath

        OPTIONAL MODIFIERS:
        - Output directory filepath
        - Forward primer sequence for extraction
        - Reverse primer sequence for extraction
        - Translating to amino acids (Y/N)
        - Retaining individual lane outputs (Y/N)
        - Number of threads
        - Extra flags for PANDASeq (use quotes, e.g. "-L 50")
        - Run Enrichment Analysis (Y/N)
        """

        QMessageBox.information(self, "Help", help_text)

    def closeEvent(self, event: QCloseEvent) -> None: # pylint: disable=invalid-name
        """
        Handle the event when the application window is closed,
        ensuring the interaction button is disabled in the main window
        and the submit button is enabled in the main window, if and only if
        the saved choices was successful, meaning the sorting is completed.
        """
        # Ensure the parent exists and the button exists before trying to disable it
        if (self.parent() is not None):
            self.parent().close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EasyDiver()
    sys.exit(app.exec_())
