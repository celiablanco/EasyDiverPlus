import os
import subprocess
from PyQt5.QtWidgets import QWidget, QMessageBox, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal


class SSAILRWorkerThread(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int)

    def __init__(self, run_script):
        super().__init__()
        self.run_script = run_script

    def run(self):
        try:
            process = subprocess.Popen(
                self.run_script.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    self.output_signal.emit(output.strip())
            self.finished_signal.emit(process.returncode)
        except Exception as e:
            self.output_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit(1)


class SSAILR(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.graph_tasks = []

    def calculate(
        self, output_dir, precision, output_text: QTextEdit, finished_callback
    ):
        run_script = "python3 modified_counts.py"

        if not os.path.exists(output_dir):
            QMessageBox.critical(self, "Error", "Output directory doesn't exist.")
            return

        print(f"{output_dir} exists.")
        run_script += f" -dir {output_dir}"
        run_script += f" -precision {precision}"
        print(run_script)

        self.start_worker(run_script, output_text, finished_callback)

    def generate_graphs(
        self,
        output_dir,
        generate_scatter_plot,
        generate_histos,
        output_text: QTextEdit,
        finished_callback,
    ):
        print(f"Current graph directory: {output_dir}.")

        self.graph_tasks = []
        for i in range(1, 4):
            if not generate_scatter_plot and i == 1:
                continue
            if not generate_histos and (i == 2 or i == 3):
                continue

            run_script = f"python3 graphs.py {output_dir} {i}"
            print(run_script)

            self.graph_tasks.append((run_script, i))

        self.process_next_graph(output_text, finished_callback)

    def process_next_graph(self, output_text, finished_callback):
        if self.graph_tasks:
            run_script, graph_type = self.graph_tasks.pop(0)
            self.start_worker(
                run_script,
                output_text,
                lambda returncode: self.on_graph_finish(
                    returncode, graph_type, output_text, finished_callback
                ),
            )
        else:
            finished_callback(0)

    def on_graph_finish(self, returncode, graph_type, output_text, finished_callback):
        if returncode == 0:
            if not self.graph_tasks and graph_type == 3:
                finished_callback(0)
        else:
            QMessageBox.critical(
                self,
                "Error",
                "An error occurred during graph generation. Please check the logs for more details.",
            )
            finished_callback(1)
        self.process_next_graph(output_text, finished_callback)

    def start_worker(self, run_script, output_text, finish_callback):
        if self.worker is not None:
            self.worker.wait()

        self.worker = SSAILRWorkerThread(run_script)
        self.worker.output_signal.connect(output_text.append)
        self.worker.output_signal.connect(print)
        self.worker.finished_signal.connect(finish_callback)
        self.worker.start()
