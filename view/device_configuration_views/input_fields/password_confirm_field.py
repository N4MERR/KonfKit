from .password_field import PasswordField

class PasswordConfirmField(PasswordField):
    """
    Field that ensures content matches a linked PasswordField and syncs its state.
    """

    def __init__(self, label_text, target_field, is_optional=True, parent=None):
        """
        Initializes the password confirmation field.
        """
        self.target_field = target_field
        super().__init__(label_text, is_optional, parent)
        self.set_error_message("Passwords do not match")
        self.radio.setEnabled(False)
        self.target_field.radio.toggled.connect(self.radio.setChecked)

    def validate(self):
        """
        Validates that the confirmation password matches the target field.
        """
        if self.target_field.radio.isChecked():
            val = self.get_value()
            if not self._run_validation(val):
                self.highlight_error(self.error_message)
                return False
        return True

    def _run_validation(self, value):
        """
        Checks if the value matches the target field value.
        """
        return value == self.target_field.get_value() and bool(value)