from .base_input_field import BaseInputField
from utils.input_validator import InputValidator


class AdaptiveIPAddressField(BaseInputField):
    """
    Field validated dynamically for either IPv4 or IPv6 formats.
    """

    def __init__(self, label_text, is_optional=False, parent=None):
        """
        Initializes the adaptive IP address field with a standard validation error message.
        """
        super().__init__(label_text, is_optional, parent)
        self.error_message = "Invalid IP address"

    def _run_validation(self, value):
        """
        Validates if the input is a valid IPv4 or IPv6 address.
        """
        return InputValidator.is_valid_ip(value) or InputValidator.is_valid_ipv6(value)

    def get_ip_version(self) -> str:
        """
        Returns the detected IP version string based on the current input value.
        """
        value = self.get_value()
        if InputValidator.is_valid_ip(value):
            return "ipv4"
        if InputValidator.is_valid_ipv6(value):
            return "ipv6"
        return "unknown"