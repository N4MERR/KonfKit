import sys
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QSize

class ProgressDialog(QDialog):
    """
    A small, modal popup window used to indicate background activity such as connecting or uploading.
    """
    def __init__(self, message="Processing...", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Please Wait")
        self.setFixedSize(QSize(250, 100))
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setModal(True)
        self._setup_ui(message)

    def _setup_ui(self, message):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.layout.addWidget(self.progress)

    def update_message(self, message):
        """
        Updates the text displayed in the progress window.
        """
        self.label.setText(message)