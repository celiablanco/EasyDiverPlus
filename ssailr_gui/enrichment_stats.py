import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QInputDialog, QFileDialog

class EnrichmentStats(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Find Enrichments")
        layout = QVBoxLayout()

        self.show_find_enrichments()

        self.setLayout(layout)

    def show_find_enrichments(self):
        calculate_enrichment = QMessageBox.question(self, "Find Enrichments", "Calculate enrichment statistics for amino acid counts? (Yes - AA, No - Nucleotide)", QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
        
        if calculate_enrichment == QMessageBox.Yes:
            self.show_output_directory_dialog("AA")
        else:
            self.show_output_directory_dialog("Nucleotides")
        
    def show_output_directory_dialog(self, type):
        script = "modified_counts.py"
        if type == "AA":
            pass
        else:
            pass
            
        # text, ok = QInputDialog.getText(self, window_title, "Enter output directory filepath")
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if output_dir:
            print(output_dir)
            subprocess.run(["python3", script])
        