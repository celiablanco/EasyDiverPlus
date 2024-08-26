#!/usr/bin/python
import os
import csv
from PyQt5.QtWidgets import ( # type: ignore # pylint: disable=import-error
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QSpinBox,
    QMessageBox, QAbstractItemView, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, QEvent # type: ignore # pylint: disable=import-error
from PyQt5.QtGui import QCloseEvent # type: ignore # pylint: disable=import-error


class SortingApp(QWidget):
    """
    A PyQt5 application for sorting files into multiple rounds.

    Attributes:
        selected_directory (str): The directory containing files to be sorted.
        output_directory (str): The directory where sorted files will be saved.
        saved_choices (bool): Indicator if the user's choices have been saved.
        round_widgets (list): List of widgets for each sorting round.

    Methods:
        __init__(self, parent: QWidget, selected_directory: str, output_directory: str) -> None:
            Initialize the SortingApp with the parent widget, 
            selected directory, and output directory.
        
        initialize_user_interface(self) -> None:
            Initialize the user interface of the SortingApp.
        
        start_sorting(self) -> None:
            Start the sorting process based on user inputs.
        
        save_choices(self) -> None:
            Save the user's sorting choices to a CSV file.
        
        center_window(self) -> None:
            Center the application window on the screen.
        
        closeEvent(self, event: QCloseEvent) -> None:
            Handle the event when the application window is closed.
        
        create_list_widget(self) -> QListWidget:
            Create and configure a QListWidget for file sorting.
        
        create_separator(self) -> QFrame:
            Create a horizontal separator line.
        
        create_drop_event(self, list_widget: QListWidget) -> QEvent:
            Create a drop event handler for a QListWidget.
    """
    def __init__(self, parent: QWidget, selected_directory: str, output_directory: str) -> None:
        """
        Initialize the SortingApp with the parent widget, selected directory, and output directory.
        """
        super().__init__(parent)
        self.selected_directory = selected_directory
        self.output_directory = output_directory if output_directory != '' else 'pipeline_output'
        self.initialize_user_interface()
        self.saved_choices = False
        self.round_widgets = []

    def initialize_user_interface(self) -> None:
        """
        Initialize the user interface of the SortingApp.
        """
        self.layout = QVBoxLayout()

        # Question 1: How many rounds?
        rounds_layout = QHBoxLayout()
        rounds_label = QLabel('How many rounds?')
        self.rounds_input = QSpinBox()
        self.rounds_input.setRange(1, 100)
        self.rounds_input.setValue(1)
        rounds_layout.addWidget(rounds_label)
        rounds_layout.addWidget(self.rounds_input)
        self.layout.addLayout(rounds_layout)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.start_sorting_button = QPushButton('Start Sorting')
        self.start_sorting_button.clicked.connect(self.start_sorting)
        buttons_layout.addWidget(self.start_sorting_button)
        self.layout.addLayout(buttons_layout)

        # File sorting interface (initially hidden)
        self.files_list = QListWidget()
        self.files_list.setDragEnabled(True)
        self.files_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.files_list.hide()
        self.layout.addWidget(self.files_list)

        # Scroll area for rounds
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.button_layout = QHBoxLayout()

        # Cancel
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setToolTip("Click to cancel and close the application.")
        self.cancel_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton('Save Choices and Continue')
        self.save_button.hide()
        self.save_button.clicked.connect(self.save_choices)
        self.button_layout.addWidget(self.save_button)
        
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)
        self.setWindowTitle('File Sorting Interface')
        self.resize(800,600)
        self.center_window()
        self.setWindowFlags(Qt.Window)

    def start_sorting(self) -> None:
        """
        Start the sorting process based on user inputs.
        """
        self.files_list.clear()

        # Clear the previous rounds layout
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            widget_to_remove = item.widget()
            if widget_to_remove is not None:
                self.scroll_layout.removeWidget(widget_to_remove)
                widget_to_remove.setParent(None)
            else:
                self.scroll_layout.removeItem(item)

        self.files_list.show()
        self.save_button.show()

        files = [
            file.split('_L001')[0]
            for file in os.listdir(self.selected_directory)
            if 'fastq' in file and not file.startswith('.')
                and not os.path.isdir(os.path.join(self.selected_directory, file))
        ]
        self.files_list.addItems(sorted(list(set(files))))

        num_rounds = int(self.rounds_input.value())

        for round_num in range(1, num_rounds + 1):
            round_label = QLabel(f'Round {round_num}')
            self.scroll_layout.addWidget(round_label)

            round_layout = QHBoxLayout()

            # In list
            pre_label = QLabel('Pre:')
            pre_list = self.create_list_widget()
            round_layout.addWidget(pre_label)
            round_layout.addWidget(pre_list)

            # Out list
            post_label = QLabel('Post:')
            post_list = self.create_list_widget()
            round_layout.addWidget(post_label)
            round_layout.addWidget(post_list)

            # Neg list
            neg_label = QLabel('Neg:')
            neg_list = self.create_list_widget()
            round_layout.addWidget(neg_label)
            round_layout.addWidget(neg_list)

            self.round_widgets.append({
                'pre': pre_list,
                'post': post_list,
                'neg': neg_list
            })

            self.scroll_layout.addLayout(round_layout)
            self.scroll_layout.addWidget(self.create_separator())

    def create_list_widget(self) -> QListWidget:
        """
        Create and configure a QListWidget for file sorting.

        Returns:
            QListWidget: Configured list widget.
        """
        list_widget = QListWidget()
        list_widget.setDragEnabled(True)
        list_widget.setAcceptDrops(True)
        list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        list_widget.dropEvent = self.create_drop_event(list_widget)
        return list_widget

    def create_separator(self) -> QFrame:
        """
        Create a horizontal separator line.

        Returns:
            QFrame: Configured frame used as a separator line.
        """
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def create_drop_event(self, list_widget: QListWidget) -> QEvent:
        """
        Create a drop event handler for a QListWidget.

        Args:
            list_widget (QListWidget): The list widget to which the drop event handler
                will be assigned.

        Returns:
            QEvent: Configured drop event handler.
        """
        def drop_event(event):
            source = event.source()
            items = source.selectedItems()

            for item in items:
                source.takeItem(source.row(item))
                list_widget.addItem(item.text())

        return drop_event

    def save_choices(self) -> None:
        """
        Save the user's sorting choices to a CSV file.
        """
        save_directory = f"{self.selected_directory}/{self.output_directory}"
        save_path = f"{save_directory}/enrichment_analysis_file_sorting_logic.csv"
        os.makedirs(save_directory, exist_ok=True)
        with open(save_path, mode='w', newline='', encoding = 'utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['filename', 'round_number', 'file_type'])

            for round_num, widgets in enumerate(self.round_widgets, start=1):
                # Save 'pre' files
                for i in range(widgets['pre'].count()):
                    item = widgets['pre'].item(i)
                    writer.writerow([item.text(), round_num, 'pre'])

                # Save 'post' files
                for i in range(widgets['post'].count()):
                    item = widgets['post'].item(i)
                    writer.writerow([item.text(), round_num, 'post'])

                # Save 'neg' files, if applicable
                if widgets['neg']:
                    for i in range(widgets['neg'].count()):
                        item = widgets['neg'].item(i)
                        writer.writerow([item.text(), round_num, 'negative'])
        self.saved_choices = True
        QMessageBox.information(self, 'Saved', 'Choices have been saved successfully!')
        self.close()

    def center_window(self) -> None:
        """
        Center the application window on the screen.
        """
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
        if (self.parent() is not None and
            hasattr(self.parent(), 'interaction_button') and
            self.saved_choices is True):
            self.parent().interaction_button.setDisabled(True)
            self.parent().submit_button.setDisabled(False)
        event.accept()
