from PySide6.QtWidgets import QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from .base_input_field import BaseConfigField

class PasswordField(BaseConfigField):
    """
    Field with hidden text and a toggle button to show/hide.
    """

    def _create_input_widget(self):
        """
        Creates a password line edit with a visibility toggle.
        """
        widget = QLineEdit()
        widget.setEchoMode(QLineEdit.Password)
        self.toggle_btn = QPushButton("Show", widget)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; font-size: 11px; font-weight: bold; padding: 0px 5px; }")
        self.toggle_btn.toggled.connect(lambda checked: (
            widget.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password),
            self.toggle_btn.setText("Hide" if checked else "Show")
        ))
        inner_layout = QHBoxLayout(widget)
        inner_layout.setContentsMargins(0, 0, 2, 0)
        inner_layout.addStretch()
        inner_layout.addWidget(self.toggle_btn)
        widget.setTextMargins(0, 0, 35, 0)
        return widget