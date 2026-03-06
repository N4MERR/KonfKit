from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel

class RangeField(QWidget):
    """
    Groups two numeric inputs on a single line for ranges (e.g., VTY lines).
    """

    def __init__(self, label_text, start_key, end_key, parent_view, is_optional=False, parent=None):
        """
        Initializes the range field.
        """
        super().__init__(parent)
        self.is_optional = is_optional
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
        if not s.strip() and not e.strip():
            if not self.is_optional:
                self.highlight_error("Both values are required.")
                return False
            return True
        if not s.strip() or not e.strip():
            self.highlight_error("Both start and end values must be provided.")
            return False
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