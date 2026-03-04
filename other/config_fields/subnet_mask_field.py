from .base_config_field import BaseConfigField
from utils.input_validator import InputValidator

class SubnetMaskField(BaseConfigField):
    """
    Field validated for contiguous subnet mask format.
    """

    def _run_validation(self, value):
        """
        Validates if the input is a valid subnet mask.
        """
        return InputValidator.is_valid_mask(value)