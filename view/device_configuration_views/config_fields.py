from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QRadioButton, QCheckBox, QLabel, \
    QPushButton, QComboBox
from PySide6.QtCore import Qt, QEvent
from utils.input_validator import InputValidator


class BaseConfigField(QWidget):
    """
    Base class for specific configuration fields providing validation and error reporting.
    """

    def __init__(self, label_text, is_optional=False, parent=None):
        """
        Initializes the base configuration field with a checkbox indicator.
        """
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

        self.radio = QCheckBox()
        self.radio.setToolTip("Enable/Disable field")
        if not is_optional:
            policy = self.radio.sizePolicy()
            policy.setRetainSizeWhenHidden(True)
            self.radio.setSizePolicy(policy)
            self.radio.hide()

        self.header_layout.addStretch()
        self.header_layout.addWidget(self.radio)
        self.layout.addWidget(self.header_container)

        self.input_widget = self._create_input_widget()
        self.layout.addWidget(self.input_widget)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red; font-size: 12px; font-weight: bold;")
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
        Creates and returns the input widget.
        """
        return QLineEdit()

    def _setup_connections(self):
        """
        Sets up signal connections for the input widget.
        """
        if isinstance(self.input_widget, QTextEdit):
            self.input_widget.textChanged.connect(lambda: self.radio.setChecked(bool(self.input_widget.toPlainText())))
            self.input_widget.textChanged.connect(self.clear_highlight)
        elif isinstance(self.input_widget, QComboBox):
            self.input_widget.currentIndexChanged.connect(lambda: self.radio.setChecked(True))
            self.input_widget.currentIndexChanged.connect(self.clear_highlight)
        else:
            self.input_widget.textChanged.connect(lambda text: self.radio.setChecked(bool(text)))
            self.input_widget.textChanged.connect(self.clear_highlight)

    def validate(self):
        """
        Validates the input field.
        """
        if self.is_optional and not self.radio.isChecked():
            return True
        val = self.get_value()
        if not self._run_validation(val):
            self.highlight_error(self.error_message)
            return False
        return True

    def _run_validation(self, value):
        """
        Runs the specific validation logic.
        """
        return bool(str(value).strip())

    def get_value(self):
        """
        Retrieves the current value from the input widget.
        """
        if isinstance(self.input_widget, QTextEdit):
            return self.input_widget.toPlainText()
        if isinstance(self.input_widget, QComboBox):
            return self.input_widget.currentText()
        return self.input_widget.text()

    def reset(self):
        """
        Resets the input field to its default state.
        """
        if isinstance(self.input_widget, QTextEdit):
            self.input_widget.clear()
        elif isinstance(self.input_widget, QComboBox):
            self.input_widget.setCurrentIndex(0)
        else:
            self.input_widget.setText("")
        self.radio.setChecked(False)
        self.clear_highlight()

    def highlight_error(self, message):
        """
        Highlights the field with an error message.
        """
        self.error_label.setText(message)
        self.error_label.show()
        self.input_widget.setStyleSheet("border: 1px solid red; background-color: rgba(255, 0, 0, 0.1);")

    def clear_highlight(self):
        """
        Clears the error highlight from the field.
        """
        self.error_label.hide()
        self.input_widget.setStyleSheet("")


class ToggleField(BaseConfigField):
    """
    A simple checkable field for binary settings like 'Shutdown' or 'Routing Enabled'.
    """

    def _create_input_widget(self):
        """
        Creates a radio button as the primary input widget.
        """
        self.option = QRadioButton("Enabled")
        return self.option

    def get_value(self):
        """
        Retrieves the boolean state of the radio button.
        """
        return self.option.isChecked()

    def _run_validation(self, value):
        """
        Validates the toggle field. Always returns True.
        """
        return True


class DropdownField(BaseConfigField):
    """
    Field using a QComboBox for selection.
    """

    def __init__(self, label_text, options, is_optional=False, parent=None):
        """
        Initializes the dropdown field with options.
        """
        self.options = options
        super().__init__(label_text, is_optional, parent)

    def _create_input_widget(self):
        """
        Creates a combobox as the input widget.
        """
        combo = QComboBox()
        combo.addItems(self.options)
        return combo


class RangeField(QWidget):
    """
    Groups two numeric inputs on a single line for ranges (e.g., VTY lines).
    """

    def __init__(self, label_text, start_key, end_key, parent_view, parent=None):
        """
        Initializes the range field.
        """
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label_text)
        self.layout.addWidget(self.label)

        self.row_layout = QHBoxLayout()
        self.start_field = QLineEdit()
        self.start_field.setPlaceholderText("Start")
        self.end_field = QLineEdit()
        self.end_field.setPlaceholderText("End")

        self.row_layout.addWidget(self.start_field)
        self.row_layout.addWidget(QLabel("-"))
        self.row_layout.addWidget(self.end_field)
        self.layout.addLayout(self.row_layout)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red; font-size: 12px; font-weight: bold;")
        self.error_label.hide()
        self.layout.addWidget(self.error_label)

        parent_view.fields[start_key] = self
        parent_view.fields[end_key] = self
        self.start_key = start_key
        self.end_key = end_key
        self.start_field.textChanged.connect(self.clear_highlight)
        self.end_field.textChanged.connect(self.clear_highlight)

    def validate(self):
        """
        Validates the range inputs.
        """
        s, e = self.start_field.text(), self.end_field.text()
        if not (s.strip() or e.strip()):
            return True
        if not (s.isdigit() and e.isdigit()):
            self.highlight_error("Both values must be numbers.")
            return False
        if int(s) > int(e):
            self.highlight_error("Start cannot be greater than end.")
            return False
        return True

    def highlight_error(self, message):
        """
        Highlights the range fields with an error.
        """
        self.error_label.setText(message)
        self.error_label.show()
        style = "border: 1px solid red; background-color: rgba(255, 0, 0, 0.1);"
        self.start_field.setStyleSheet(style)
        self.end_field.setStyleSheet(style)

    def clear_highlight(self):
        """
        Clears the error highlight from the range fields.
        """
        self.error_label.hide()
        self.start_field.setStyleSheet("")
        self.end_field.setStyleSheet("")


class IPAddressField(BaseConfigField):
    """
    Field validated for IPv4 format.
    """

    def _run_validation(self, value):
        """
        Validates if the input is a valid IP address.
        """
        return InputValidator.is_valid_ip(value)


class SubnetMaskField(BaseConfigField):
    """
    Field validated for contiguous subnet mask format.
    """

    def _run_validation(self, value):
        """
        Validates if the input is a valid subnet mask.
        """
        return InputValidator.is_valid_mask(value)


class WildcardMaskField(BaseConfigField):
    """
    Field validated for contiguous wildcard mask format.
    """

    def _run_validation(self, value):
        """
        Validates if the input is a valid wildcard mask.
        """
        return InputValidator.is_valid_wildcard_mask(value)


class MacAddressField(BaseConfigField):
    """
    Field validated for standard Cisco MAC address formats.
    """

    def _run_validation(self, value):
        """
        Validates if the input is a valid MAC address.
        """
        return InputValidator.is_valid_mac_address(value)


class InterfaceField(BaseConfigField):
    """
    Field validated for standard Cisco interface names.
    """

    def _run_validation(self, value):
        """
        Validates if the input is a valid interface name.
        """
        return InputValidator.is_valid_interface_name(value)


class NumberField(BaseConfigField):
    """
    Field validated for numeric input.
    """

    def _run_validation(self, value):
        """
        Validates if the input is a valid number.
        """
        return InputValidator.is_valid_number(value)


class RangedNumberField(BaseConfigField):
    """
    Field validated for numeric input within a specific range.
    """

    def __init__(self, label_text, min_val, max_val, is_optional=False, parent=None):
        """
        Initializes the ranged number field with minimum and maximum constraints.
        """
        self.min_val = min_val
        self.max_val = max_val
        super().__init__(label_text, is_optional, parent)
        self.set_error_message(f"Value must be between {self.min_val} and {self.max_val}")

    def _run_validation(self, value):
        """
        Validates if the input is a number within the defined range.
        """
        return InputValidator.is_in_range(value, self.min_val, self.max_val)


class PasswordField(BaseConfigField):
    """
    Field with hidden text and a toggle button to show/hide.
    """

    def _create_input_widget(self):
        """
        Creates a password line edit with a visibility toggle.
        """
        widget = QLineEdit()
        widget.setEchoMode(QLineEdit.Password)
        self.toggle_btn = QPushButton("Show", widget)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; font-size: 11px; font-weight: bold; padding: 0px 5px; }")
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


class MultilineField(BaseConfigField):
    """
    Field using QTextEdit for multi-line configurations.
    """

    def _create_input_widget(self):
        """
        Creates a text edit for multiline input.
        """
        widget = QTextEdit()
        widget.setMinimumHeight(150)
        return widget


class RadioIndicatorField(QWidget):
    """
    A standalone checkbox field for binary global settings.
    """

    def __init__(self, label_text, parent=None):
        """
        Initializes the standalone checkbox indicator field.
        """
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 10)
        self.radio = QCheckBox(label_text)
        self.layout.addWidget(self.radio)

    def isChecked(self):
        """
        Retrieves the boolean state of the checkbox.
        """
        return self.radio.isChecked()