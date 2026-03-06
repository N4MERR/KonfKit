from .base_input_field import BaseConfigField
from utils.input_validator import InputValidator

class RangedNumberField(BaseConfigField):
    """
    Field validated for numeric input within a specific range.
    """

    def __init__(self, label_text, min_val, max_val, is_optional=False, parent=None):
        """
        Initializes the ranged number field with minimum and maximum constraints.
        """
        self.min_val = min_val
        self.max_val = max_val
        super().__init__(label_text, is_optional, parent)
        self.set_error_message(f"Value must be between {self.min_val} and {self.max_val}")

    def _run_validation(self, value):
        """
        Validates if the input is a number within the defined range.
        """
        return InputValidator.is_in_range(value, self.min_val, self.max_val)