from .base_input_field import BaseInputField
from utils.input_validator import InputValidator


class AdaptiveSubnetMaskField(BaseInputField):
    """
    Field validated dynamically for either a contiguous IPv4 subnet mask or an IPv6 prefix length.
    """

    def __init__(self, label_text, is_optional=False, parent=None, linked_ip_field=None):
        """
        Initializes the adaptive mask field with a standard dual-stack error message and optional linkage.
        """
        super().__init__(label_text, is_optional, parent)
        self.error_message = "Invalid mask or prefix"

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
        Validates if the input is a valid subnet mask or IPv6 prefix length.
        """
        return InputValidator.is_valid_mask(value) or InputValidator.is_valid_ipv6_prefix(value)