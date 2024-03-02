import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox

from easy_diver import EasyDiver
from enrichment_stats import EnrichmentStats

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Main Menu")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        options = ["Run All", "Use EasyDIVER", "Calculate Enrichment Statistics", "Figures and Misc.", "Help", "Quit"]
        for option in options:
            button = QPushButton(option, self)
            if option == "Use EasyDIVER":
                button.clicked.connect(self.easy_diver)
                
            if option == "Calculate Enrichment Statistics":
                button.clicked.connect(self.calculate_enrichment_statistics)

            if option == "Help":
                button.clicked.connect(self.display_help_message) 

            if option == "Quit":
                button.clicked.connect(self.exit_application)

            layout.addWidget(button)

        self.setLayout(layout)
        self.show()

    def run_all(self):
        pass

    def easy_diver(self):
        self.easy_diver_widget = EasyDiver()
        self.easy_diver_widget.show()

    def calculate_enrichment_statistics(self):
        self.enrichment_stats_widget = EnrichmentStats()
        self.enrichment_stats_widget.show()

    def display_figures(self):
        pass

    def display_help_message(self):
        help_text = """
        SimpleSAILR is a Bash program that takes input files of SELEX round reads in fastq(.gz) format and analyzes them, providing:
        - Sequence type and length distribution
        - Joined reads
        - Enrichment information
        There are also options to visualize sequence distribution, enrichment, and diversity data.

        Version 2.0
        Author: Allison Tee and Celia Blanco
        Contact: ateecup@stanford.edu or celia.blanco@bmsis.org

        REQUIRED:
        - Input directory filepath

        OPTIONAL MODIFIERS:
        - Output directory filepath
        - Forward primer sequence for extraction
        - Reverse primer sequence for extraction
        - Translating to amino acids
        - Retaining individual lane outputs
        - Number of threads
        - Extra flags for PANDASeq (use quotes, e.g. "-L 50")
        """

        QMessageBox.information(self, "Help", help_text)

    def exit_application(self):
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainMenu()
    sys.exit(app.exec_())