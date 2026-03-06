from .base_input_field import BaseConfigField
from utils.input_validator import InputValidator

class SubnetMaskField(BaseConfigField):
    """
    Field validated for contiguous subnet mask format.
    """

    def __init__(self, label_text, is_optional=False, parent=None):
        """
        Initializes the subnet mask field with a specific error message.
        """
        super().__init__(label_text, is_optional, parent)
        self.error_message = "Invalid subnet mask"

    def _run_validation(self, value):
        """
        Validates if the input is a valid subnet mask.
        """
        return InputValidator.is_valid_mask(value)