from .base_input_field import BaseInputField
from utils.input_validator import InputValidator

class WildcardMaskField(BaseInputField):
    """
    Field validated for contiguous wildcard mask format.
    """

    def _run_validation(self, value):
        """
        Validates if the input is a valid wildcard mask.
        """
        return InputValidator.is_valid_wildcard_mask(value)