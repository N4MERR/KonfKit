from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QCheckBox, QLabel, QComboBox
from PySide6.QtCore import Qt, QEvent

class BaseInputField(QWidget):
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