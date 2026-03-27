from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression
from .base_input_field import BaseInputField
from utils.input_validator import InputValidator


class AdaptiveWildcardMaskField(BaseInputField):
    """
    Field validated dynamically for either an IPv4 wildcard mask or an IPv6 prefix length.
    """

    def __init__(self, label_text, is_optional=False, parent=None, linked_ip_field=None):
        """
        Initializes the adaptive wildcard mask field with a standard dual-stack error message.
        """
        super().__init__(label_text, is_optional, parent)
        self.error_message = "Invalid wildcard, prefix length"

        regex = QRegularExpression(r"^[a-zA-Z0-9.]*$")
        validator = QRegularExpressionValidator(regex, self)
        self.input_widget.setValidator(validator)

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
        Validates if the input is a valid wildcard mask, IPv6 prefix length, or keyword.
        """
        val_str = str(value).strip().lower()
        if val_str in ["any", "host"]:
            return True
        return InputValidator.is_valid_wildcard_mask(value) or InputValidator.is_valid_ipv6_prefix(value)