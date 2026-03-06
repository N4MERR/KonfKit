from .base_input_field import BaseConfigField
from utils.input_validator import InputValidator

class IPv6PrefixField(BaseConfigField):
    """
    Field for IPv6 prefix length that enforces a leading forward slash.
    """

    def __init__(self, label_text, is_optional=False, parent=None, linked_ip_field=None):
        """
        Initializes the prefix field with a forced '/' prefix, range validation, and optional linkage.
        """
        super().__init__(label_text, is_optional, parent)
        self.error_message = "Prefix must be /0 to /64"
        self.input_widget.setText("/")
        self.input_widget.textChanged.connect(self._ensure_prefix)

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
            self.input_widget.setText("/")

    def _ensure_prefix(self, text):
        """
        Prevents the user from removing the leading slash.
        """
        if not text.startswith("/"):
            self.input_widget.setText("/" + text.lstrip("/"))

    def validate(self):
        """
        Validates the input only if the widget is enabled.
        """
        if not self.input_widget.isEnabled():
            return True
        return super().validate()

    def _run_validation(self, value):
        """
        Validates if the numerical part of the prefix is between 0 and 64.
        """
        return InputValidator.is_valid_ipv6_prefix(value)