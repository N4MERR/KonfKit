from .base_config_field import BaseConfigField
from utils.input_validator import InputValidator

class InterfaceField(BaseConfigField):
    """
    Field validated for standard Cisco interface names.
    """

    def _run_validation(self, value):
        """
        Validates if the input is a valid interface name.
        """
        return InputValidator.is_valid_interface_name(value)