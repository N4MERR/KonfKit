from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression
from .base_input_field import BaseInputField
from utils.input_validator import InputValidator

class NumberField(BaseInputField):
    """
    Field validated for numeric input.
    """

    def __init__(self, label_text, is_optional=False, parent=None):
        """
        Initializes the number field and restricts input to digits only.
        """
        super().__init__(label_text, is_optional, parent)
        self.error_message = "Invalid number"
        regex = QRegularExpression(r"^\d*$")
        validator = QRegularExpressionValidator(regex, self)
        self.input_widget.setValidator(validator)

    def _run_validation(self, value):
        """
        Validates if the input is a valid number.
        """
        return InputValidator.is_valid_number(value)