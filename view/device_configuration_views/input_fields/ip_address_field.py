from .base_input_field import BaseConfigField
from utils.input_validator import InputValidator

class IPAddressField(BaseConfigField):
    """
    Field validated for IPv4 format.
    """

    def __init__(self, label_text, is_optional=False, parent=None):
        """
        Initializes the IP address field with a specific error message.
        """
        super().__init__(label_text, is_optional, parent)
        self.error_message = "Invalid IP address"

    def _run_validation(self, value):
        """
        Validates if the input is a valid IP address.
        """
        return InputValidator.is_valid_ip(value)