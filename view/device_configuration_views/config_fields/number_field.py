from .base_config_field import BaseConfigField
from utils.input_validator import InputValidator

class NumberField(BaseConfigField):
    """
    Field validated for numeric input.
    """

    def _run_validation(self, value):
        """
        Validates if the input is a valid number.
        """
        return InputValidator.is_valid_number(value)