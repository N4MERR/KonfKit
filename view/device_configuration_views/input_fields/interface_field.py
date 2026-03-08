from .base_input_field import BaseInputField
from utils.input_validator import InputValidator

class InterfaceField(BaseInputField):
    """
    Field validated for standard Cisco interface names.
    """

    def _run_validation(self, value):
        """
        Validates if the input is a valid interface name.
        """
        return InputValidator.is_valid_interface_name(value)