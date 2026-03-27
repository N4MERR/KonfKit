from PySide6.QtWidgets import QTextEdit
from .base_input_field import BaseInputField

class MultilineField(BaseInputField):
    """
    Field using QTextEdit for multi-line configurations.
    """

    def __init__(self, label_text, is_optional=False, parent=None):
        """
        Initializes the multiline field with a specific error message.
        """
        super().__init__(label_text, is_optional, parent)
        self.error_message = "Input cannot be empty"

    def _create_input_widget(self):
        """
        Creates a text edit for multiline input.
        """
        widget = QTextEdit()
        widget.setMinimumHeight(150)
        return widget