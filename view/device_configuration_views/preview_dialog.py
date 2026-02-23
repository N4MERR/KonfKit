from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QPlainTextEdit, QLabel, QFrame
from PySide6.QtCore import Qt


class PreviewDialog(QDialog):
    """
    A modern, styled dialog designed to display configuration commands in a terminal-like interface.

    This dialog provides a high-contrast preview of CLI commands and offers
    the user the choice to proceed with the application or cancel.
    """

    def __init__(self, commands_text: str, parent=None):
        """
        Initializes the PreviewDialog with stylized components and layout.
        """
        super().__init__(parent)
        self.setWindowTitle("Configuration Preview")
        self.resize(700, 500)
        self.setMinimumSize(500, 400)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.setStyleSheet("background-color: #2b2b2b;")

        self.header_label = QLabel("Configuration Preview")
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("""
            color: #ffffff;
            font-size: 13pt;
            font-weight: bold;
            padding-bottom: 10px;
        """)
        self.main_layout.addWidget(self.header_label)

        self.console_output = QPlainTextEdit()
        self.console_output.setFrameShape(QFrame.NoFrame)
        self.console_output.setReadOnly(True)
        self.console_output.setCursorWidth(2)
        self.console_output.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByKeyboard |
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.console_output.setFocusPolicy(Qt.StrongFocus)
        self.console_output.setPlainText(commands_text)

        self.apply_terminal_style()
        self.main_layout.addWidget(self.console_output)

        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 15, 0, 0)
        self.button_layout.setSpacing(10)

        self.close_btn = QPushButton("Cancel")
        self.apply_btn = QPushButton("Apply Configuration")

        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.apply_btn.setCursor(Qt.PointingHandCursor)

        self.close_btn.setMinimumHeight(35)
        self.apply_btn.setMinimumHeight(35)

        self.apply_button_styles()

        self.close_btn.clicked.connect(self.reject)
        self.apply_btn.clicked.connect(self.accept)

        self.button_layout.addStretch()
        self.button_layout.addWidget(self.close_btn)
        self.button_layout.addWidget(self.apply_btn)

        self.main_layout.addLayout(self.button_layout)

    def apply_terminal_style(self):
        """
        Applies a dark terminal aesthetic to the QPlainTextEdit component.
        """
        self.console_output.setStyleSheet("""
            QPlainTextEdit {
                background-color: #121212;
                color: #00ff00;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 10pt;
                padding: 10px;
                border: 1px solid #444444;
                border-radius: 4px;
            }
        """)

    def apply_button_styles(self):
        """
        Applies CSS styling to the dialog buttons for a consistent UI.
        """
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: white;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)

        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border-radius: 4px;
                padding: 5px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0098ff;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)

    def get_commands(self) -> str:
        """
        Retrieves the current text content from the terminal preview window.
        """
        return self.console_output.toPlainText()