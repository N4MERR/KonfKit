from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QCheckBox, QLabel, QPushButton, QComboBox
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
        return QLineEdit()

    def _setup_connections(self):
        if isinstance(self.input_widget, QTextEdit):
            self.input_widget.textChanged.connect(lambda: self.checkbox.setChecked(bool(self.input_widget.toPlainText())))
            self.input_widget.textChanged.connect(self.clear_highlight)
        elif isinstance(self.input_widget, QComboBox):
            self.input_widget.currentIndexChanged.connect(lambda: self.checkbox.setChecked(True))
            self.input_widget.currentIndexChanged.connect(self.clear_highlight)
        else:
            self.input_widget.textChanged.connect(lambda text: self.checkbox.setChecked(bool(text)))
            self.input_widget.textChanged.connect(self.clear_highlight)

    def validate(self):
        if self.is_optional and not self.checkbox.isChecked():
            return True
        val = self.get_value()
        if not self._run_validation(val):
            self.highlight_error(self.error_message)
            return False
        return True

    def _run_validation(self, value):
        return bool(str(value).strip())

    def get_value(self):
        if isinstance(self.input_widget, QTextEdit):
            return self.input_widget.toPlainText()
        if isinstance(self.input_widget, QComboBox):
            return self.input_widget.currentText()
        return self.input_widget.text()

    def reset(self):
        if isinstance(self.input_widget, QTextEdit):
            self.input_widget.clear()
        elif isinstance(self.input_widget, QComboBox):
            self.input_widget.setCurrentIndex(0)
        else:
            self.input_widget.setText("")
        self.checkbox.setChecked(False)
        self.clear_highlight()

    def highlight_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()
        self.input_widget.setStyleSheet("border: 1px solid #ff4c4c; background-color: rgba(255, 76, 76, 0.1);")

    def clear_highlight(self):
        self.error_label.hide()
        self.input_widget.setStyleSheet("")

class ToggleField(BaseConfigField):
    """
    A simple checkable field for binary settings like 'Shutdown' or 'Routing Enabled'.
    """
    def _create_input_widget(self):
        self.check = QCheckBox("Enabled")
        return self.check

    def get_value(self):
        return self.check.isChecked()

    def _run_validation(self, value):
        return True

class DropdownField(BaseConfigField):
    """
    Field using a QComboBox for selection.
    """
    def __init__(self, label_text, options, is_optional=False, parent=None):
        self.options = options
        super().__init__(label_text, is_optional, parent)

    def _create_input_widget(self):
        combo = QComboBox()
        combo.addItems(self.options)
        return combo

class RangeField(QWidget):
    """
    Groups two numeric inputs on a single line for ranges (e.g., VTY lines).
    """
    def __init__(self, label_text, start_key, end_key, parent_view, parent=None):
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
        self.error_label.setStyleSheet("color: #ff4c4c; font-size: 12px; font-weight: bold;")
        self.error_label.hide()
        self.layout.addWidget(self.error_label)
        parent_view.fields[start_key] = self
        parent_view.fields[end_key] = self
        self.start_key = start_key
        self.end_key = end_key
        self.start_field.textChanged.connect(self.clear_highlight)
        self.end_field.textChanged.connect(self.clear_highlight)

    def validate(self):
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
        self.error_label.setText(message)
        self.error_label.show()
        style = "border: 1px solid #ff4c4c; background-color: rgba(255, 76, 76, 0.1);"
        self.start_field.setStyleSheet(style)
        self.end_field.setStyleSheet(style)

    def clear_highlight(self):
        self.error_label.hide()
        self.start_field.setStyleSheet("")
        self.end_field.setStyleSheet("")

class IPAddressField(BaseConfigField):
    """
    Field validated for IPv4 format.
    """
    def _run_validation(self, value):
        return InputValidator.is_valid_ip(value)

class NumberField(BaseConfigField):
    """
    Field validated for numeric input.
    """
    def _run_validation(self, value):
        return InputValidator.is_valid_number(value)

class PasswordField(BaseConfigField):
    """
    Field with hidden text and a toggle button to show/hide.
    """
    def _create_input_widget(self):
        widget = QLineEdit()
        widget.setEchoMode(QLineEdit.Password)
        self.toggle_btn = QPushButton("Show", widget)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setStyleSheet("QPushButton { border: none; background: transparent; color: #a0a0a0; font-size: 11px; font-weight: bold; padding: 0px 5px; }")
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
        self.target_field = target_field
        super().__init__(label_text, is_optional, parent)
        self.set_error_message("Passwords do not match")
        self.checkbox.setEnabled(False)
        self.target_field.checkbox.toggled.connect(self.checkbox.setChecked)

    def validate(self):
        if self.target_field.checkbox.isChecked():
            val = self.get_value()
            if not self._run_validation(val):
                self.highlight_error(self.error_message)
                return False
        return True

    def _run_validation(self, value):
        return value == self.target_field.get_value() and bool(value)

class MultilineField(BaseConfigField):
    """
    Field using QTextEdit for multi-line configurations.
    """
    def _create_input_widget(self):
        widget = QTextEdit()
        widget.setMinimumHeight(150)
        return widget

class CheckboxField(QWidget):
    """
    A standalone checkbox field for binary global settings.
    """
    def __init__(self, label_text, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 10)
        self.checkbox = QCheckBox(label_text)
        self.checkbox.setStyleSheet("color: white;")
        self.layout.addWidget(self.checkbox)

    def isChecked(self):
        return self.checkbox.isChecked()