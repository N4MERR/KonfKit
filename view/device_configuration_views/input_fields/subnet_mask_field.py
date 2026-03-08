from .base_input_field import BaseInputField
from utils.input_validator import InputValidator


class SubnetMaskField(BaseInputField):
    """
    Field validated for contiguous subnet mask format.
    """

    def __init__(self, label_text, is_optional=False, parent=None, linked_ip_field=None):
        """
        Initializes the subnet mask field with a specific error message and optional linkage.
        """
        super().__init__(label_text, is_optional, parent)
        self.error_message = "Invalid subnet mask"

        if linked_ip_field:
            self.radio.show()
            self.radio.setEnabled(False)
            self.radio.setChecked(linked_ip_field.radio.isChecked())
            self.input_widget.setEnabled(linked_ip_field.radio.isChecked())
            linked_ip_field.radio.toggled.connect(self._toggle_state)

    def _toggle_state(self, checked):
        """
        Toggles the enabled state of the field based on the linked field.
        """
        self.input_widget.setEnabled(checked)
        self.radio.setChecked(checked)
        if not checked:
            self.reset()

    def validate(self):
        """
        Validates the input only if the widget is enabled.
        """
        if not self.input_widget.isEnabled():
            return True
        return super().validate()

    def _run_validation(self, value):
        """
        Validates if the input is a valid subnet mask.
        """
        return InputValidator.is_valid_mask(value)