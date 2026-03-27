from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression
from .base_input_field import BaseInputField
from utils.input_validator import InputValidator

class WildcardMaskField(BaseInputField):
    """
    Field validated for contiguous wildcard mask format.
    """

    def __init__(self, label_text, is_optional=False, parent=None):
        """
        Initializes the wildcard mask field and restricts input to numbers and dots.
        """
        super().__init__(label_text, is_optional, parent)
        self.error_message = "Invalid wildcard mask"
        regex = QRegularExpression(r"^[0-9.]*$")
        validator = QRegularExpressionValidator(regex, self)
        self.input_widget.setValidator(validator)

    def _run_validation(self, value):
        """
        Validates if the input is a valid wildcard mask.
        """
        return InputValidator.is_valid_wildcard_mask(value)