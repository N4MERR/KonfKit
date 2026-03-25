from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression
from .base_input_field import BaseInputField
from utils.input_validator import InputValidator

class IPAddressField(BaseInputField):
    """
    Field validated for IPv4 format.
    """

    def __init__(self, label_text, is_optional=False, parent=None):
        """
        Initializes the IP address field with a specific error message and restricts input to numbers and dots.
        """
        super().__init__(label_text, is_optional, parent)
        self.error_message = "Invalid IP address"
        regex = QRegularExpression(r"^[0-9.]*$")
        validator = QRegularExpressionValidator(regex, self)
        self.input_widget.setValidator(validator)

    def _run_validation(self, value):
        """
        Validates if the input is a valid IP address.
        """
        return InputValidator.is_valid_ip(value)