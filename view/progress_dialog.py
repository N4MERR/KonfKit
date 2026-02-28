import sys
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QSize

class ProgressDialog(QDialog):
    """
    A modern progress dialog with a slim loading indicator adaptable to any system theme.
    """
    def __init__(self, message="Processing...", parent=None):
        """
        Initializes the progress dialog with a given message.
        """
        super().__init__(parent)
        self.setWindowTitle("Please Wait")
        self.setFixedSize(QSize(300, 80))
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setModal(True)
        self._setup_ui(message)

    def _setup_ui(self, message):
        """
        Sets up the user interface elements for the progress dialog.
        """
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(25, 20, 25, 20)
        self.layout.setSpacing(15)

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 11pt; font-weight: bold; background: transparent;")
        self.layout.addWidget(self.label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        self.layout.addWidget(self.progress)

    def update_message(self, message):
        """
        Updates the displayed message in the dialog.
        """
        self.label.setText(message)