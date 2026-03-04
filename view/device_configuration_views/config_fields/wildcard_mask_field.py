from .base_config_field import BaseConfigField
from utils.input_validator import InputValidator

class WildcardMaskField(BaseConfigField):
    """
    Field validated for contiguous wildcard mask format.
    """

    def _run_validation(self, value):
        """
        Validates if the input is a valid wildcard mask.
        """
        return InputValidator.is_valid_wildcard_mask(value)