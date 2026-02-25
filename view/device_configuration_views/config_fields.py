from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QCheckBox, QLabel, QPushButton
from PySide6.QtCore import Qt, QEvent
from utils.input_validator import InputValidator


class BaseConfigField(QWidget):
    """
    Base class for specific configuration fields providing validation and error reporting.
    """

    def __init__(self, label_text, is_optional=False, parent=None):
        super().__init__(parent)
        self.is_optional = is_optional
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)

        self.header_container = QWidget()
        self.header_layout = QHBoxLayout(self.header_container)
        self.header_layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label_text)
        self.header_layout.addWidget(self.label)

        self.checkbox = QCheckBox()
        if not is_optional:
            policy = self.checkbox.sizePolicy()
            policy.setRetainSizeWhenHidden(True)
            self.checkbox.setSizePolicy(policy)
            self.checkbox.hide()

        self.header_layout.addStretch()
        self.header_layout.addWidget(self.checkbox)

        self.layout.addWidget(self.header_container)

        self.input_widget = self._create_input_widget()
        self.layout.addWidget(self.input_widget)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #ff4c4c; font-size: 12px; font-weight: bold;")
        self.error_label.hide()
        self.layout.addWidget(self.error_label)

        self.error_message = "Invalid input"
        self._setup_connections()
        self.input_widget.installEventFilter(self)

    def set_error_message(self, message):
        """
        Sets a custom error message for the validation failure.
        """
        self.error_message = message

    def eventFilter(self, source, event):
        """
        Clears highlight on click or focus.
        """
        if source is self.input_widget and (event.type() == QEvent.MouseButtonPress or event.type() == QEvent.FocusIn):
            self.clear_highlight()
        return super().eventFilter(source, event)

    def _create_input_widget(self):
        """
        Standard QLineEdit for input.
        """
        return QLineEdit()

    def _setup_connections(self):
        """
        Auto-checks checkbox and clears highlights on text change.
        """
        if isinstance(self.input_widget, QTextEdit):
            self.input_widget.textChanged.connect(lambda: self.checkbox.setChecked(bool(self.input_widget.toPlainText())))
            self.input_widget.textChanged.connect(self.clear_highlight)
        else:
            self.input_widget.textChanged.connect(lambda text: self.checkbox.setChecked(bool(text)))
            self.input_widget.textChanged.connect(self.clear_highlight)

    def validate(self):
        """
        Validates the field if it is mandatory or currently checked.
        """
        if self.is_optional and not self.checkbox.isChecked():
            return True
        val = self.get_value()
        if not self._run_validation(val):
            self.highlight_error(self.error_message)
            return False
        return True

    def _run_validation(self, value):
        """
        Checks if value is non-empty.
        """
        return bool(value.strip())

    def get_value(self):
        """
        Retrieves current text.
        """
        if isinstance(self.input_widget, QTextEdit):
            return self.input_widget.toPlainText()
        return self.input_widget.text()

    def reset(self):
        """
        Clears text and resets visual state.
        """
        if isinstance(self.input_widget, QTextEdit):
            self.input_widget.clear()
        else:
            self.input_widget.setText("")
        self.checkbox.setChecked(False)
        self.clear_highlight()

    def highlight_error(self, message):
        """
        Shows red border and error message.
        """
        self.error_label.setText(message)
        self.error_label.show()
        self.input_widget.setStyleSheet("border: 1px solid #ff4c4c; background-color: rgba(255, 76, 76, 0.1);")

    def clear_highlight(self):
        """
        Hides error state.
        """
        self.error_label.hide()
        self.input_widget.setStyleSheet("")


class IPAddressField(BaseConfigField):
    """
    Field specialized for IPv4 address validation.
    """

    def _run_validation(self, value):
        """
        Validates the input string as a valid IPv4 address.
        """
        return InputValidator.is_valid_ip(value)


class NumberField(BaseConfigField):
    """
    Field specialized for numeric input validation.
    """

    def _run_validation(self, value):
        """
        Validates the input string as a valid number.
        """
        return InputValidator.is_valid_number(value)


class PasswordField(BaseConfigField):
    """
    Field for password input with visibility toggle.
    """

    def _create_input_widget(self):
        """
        Creates a QLineEdit with password echo mode and a show/hide button.
        """
        widget = QLineEdit()
        widget.setEchoMode(QLineEdit.Password)

        self.toggle_btn = QPushButton("Show", widget)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; color: #a0a0a0; font-size: 11px; font-weight: bold; padding: 0px 5px; }")

        self.toggle_btn.toggled.connect(lambda checked: (
            widget.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password),
            self.toggle_btn.setText("Hide" if checked else "Show")
        ))

        inner_layout = QHBoxLayout(widget)
        inner_layout.setContentsMargins(0, 0, 2, 0)
        inner_layout.addStretch()
        inner_layout.addWidget(self.toggle_btn)
        widget.setTextMargins(0, 0, 35, 0)
        return widget


class PasswordConfirmField(PasswordField):
    """
    Field for password confirmation that compares against a target field.
    """

    def __init__(self, label_text, target_field, is_optional=False, parent=None):
        self.target_field = target_field
        super().__init__(label_text, is_optional, parent)

    def validate(self):
        """
        Skips validation if the password field itself is not active.
        """
        if not self.target_field.checkbox.isChecked():
            return True
        return super().validate()

    def _run_validation(self, value):
        """
        Validates that the confirmation value matches the target field value.
        """
        return value == self.target_field.get_value() and bool(value)


class MultilineField(BaseConfigField):
    """
    Field for larger text inputs using QTextEdit.
    """

    def _create_input_widget(self):
        """
        Creates a QTextEdit widget with a minimum height.
        """
        widget = QTextEdit()
        widget.setMinimumHeight(150)
        return widget