from .base_input_field import BaseConfigField
from utils.input_validator import InputValidator

class MacAddressField(BaseConfigField):
    """
    Field validated for standard Cisco MAC address formats.
    """

    def _run_validation(self, value):
        """
        Validates if the input is a valid MAC address.
        """
        return InputValidator.is_valid_mac_address(value)