from .base_input_field import BaseInputField
from utils.input_validator import InputValidator

class NumberField(BaseInputField):
    """
    Field validated for numeric input.
    """

    def _run_validation(self, value):
        """
        Validates if the input is a valid number.
        """
        return InputValidator.is_valid_number(value)