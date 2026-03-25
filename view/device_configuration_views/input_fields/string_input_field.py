import re
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression
from .base_input_field import BaseInputField


class StringInputField(BaseInputField):
    """
    Input field for strings with configurable constraints such as maximum length, allowed characters, and starting character rules.
    """

    def __init__(self, label_text, max_length=None, allowed_chars=None, start_with=None, cant_start_with=None, is_optional=False, parent=None):
        """
        Initializes the string input field with specific character and length constraints.
        """
        super().__init__(label_text, is_optional, parent)
        self.max_length = max_length
        self.allowed_chars = allowed_chars
        self.start_with = start_with
        self.cant_start_with = cant_start_with

        self.error_message = self._generate_error_message()

        if self.max_length is not None:
            self.input_widget.setMaxLength(self.max_length)

        if self.allowed_chars:
            regex = QRegularExpression(f"^[{self.allowed_chars}]*$")
            validator = QRegularExpressionValidator(regex, self)
            self.input_widget.setValidator(validator)

    def _generate_error_message(self):
        """
        Generates a descriptive error message based on the configured constraints.
        """
        msg_parts = ["Invalid string."]
        if self.max_length:
            msg_parts.append(f"Max length: {self.max_length}.")
        if self.start_with:
            msg_parts.append(f"Must start with valid characters.")
        if self.cant_start_with:
            msg_parts.append(f"Contains invalid starting characters.")
        return " ".join(msg_parts)

    def _run_validation(self, value):
        """
        Validates the input string against all defined constraints.
        """
        if not value:
            return False

        if self.start_with and not re.match(f"^[{self.start_with}]", value):
            return False

        if self.cant_start_with and re.match(f"^[{self.cant_start_with}]", value):
            return False

        if self.allowed_chars and not re.match(f"^[{self.allowed_chars}]*$", value):
            return False

        if self.max_length and len(value) > self.max_length:
            return False

        return True