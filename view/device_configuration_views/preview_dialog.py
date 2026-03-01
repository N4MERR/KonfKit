from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QPlainTextEdit, QLabel, QFrame
from PySide6.QtCore import Qt


class PreviewDialog(QDialog):
    """
    A modern, styled dialog designed to display configuration commands in a terminal-like interface.
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

        self.header_label = QLabel("Configuration Preview")
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("font-size: 13pt; font-weight: bold; padding-bottom: 10px; background: transparent;")
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
        self.apply_btn = QPushButton("Apply")

        self.close_btn.setStyleSheet(
            "QPushButton { background-color: #d32f2f; color: white; font-weight: bold; border-radius: 4px; border: none; padding: 8px 15px; } "
            "QPushButton:hover { background-color: #b71c1c; }"
        )
        self.apply_btn.setStyleSheet(
            "QPushButton { background-color: #0078d4; color: white; font-weight: bold; border-radius: 4px; border: none; padding: 8px 15px; } "
            "QPushButton:hover { background-color: #005a9e; }"
        )

        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.apply_btn.setCursor(Qt.PointingHandCursor)

        self.close_btn.setMinimumHeight(35)
        self.apply_btn.setMinimumHeight(35)

        self.close_btn.clicked.connect(self.reject)
        self.apply_btn.clicked.connect(self.accept)

        self.button_layout.addStretch()
        self.button_layout.addWidget(self.close_btn)
        self.button_layout.addWidget(self.apply_btn)

        self.main_layout.addLayout(self.button_layout)

    def apply_terminal_style(self):
        """
        Applies a terminal aesthetic to the QPlainTextEdit component inheriting system colors.
        """
        self.console_output.setStyleSheet(
            "QPlainTextEdit { "
            "border: 1px solid rgba(128, 128, 128, 0.4); "
            "border-radius: 8px; "
            "font-family: 'Consolas', monospace; "
            "font-size: 11pt; "
            "padding: 8px; "
            "background: transparent; "
            "}"
        )

    def get_commands(self) -> str:
        """
        Retrieves the current text content from the terminal preview window.
        """
        return self.console_output.toPlainText()