from .base_config_field import BaseConfigField
from utils.input_validator import InputValidator

class IPAddressField(BaseConfigField):
    """
    Field validated for IPv4 format.
    """

    def _run_validation(self, value):
        """
        Validates if the input is a valid IP address.
        """
        return InputValidator.is_valid_ip(value)