from PySide6.QtWidgets import QTextEdit
from .base_input_field import BaseConfigField

class MultilineField(BaseConfigField):
    """
    Field using QTextEdit for multi-line configurations.
    """

    def _create_input_widget(self):
        """
        Creates a text edit for multiline input.
        """
        widget = QTextEdit()
        widget.setMinimumHeight(150)
        return widget