from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression
from .base_input_field import BaseInputField
from utils.input_validator import InputValidator


class IPv6AddressField(BaseInputField):
    """
    Field validated specifically for IPv6 format.
    """

    def __init__(self, label_text, is_optional=False, parent=None):
        """
        Initializes the IPv6 address field with a standard validation error message and restricts input to hex characters and colons.
        """
        super().__init__(label_text, is_optional, parent)
        self.error_message = "Invalid IPv6 address"
        regex = QRegularExpression(r"^[0-9a-fA-F:]*$")
        validator = QRegularExpressionValidator(regex, self)
        self.input_widget.setValidator(validator)

    def _run_validation(self, value):
        """
        Validates if the input is a valid IPv6 address.
        """
        return InputValidator.is_valid_ipv6(value)