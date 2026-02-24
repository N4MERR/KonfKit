"""
Base configuration view providing a unified layout for device settings.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFormLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt, QEvent


class BaseConfigView(QWidget):
    """
    Base class for configuration views providing a consistent layout and error highlighting mechanism.
    """

    def __init__(self, title=None):
        """
        Initializes the base view with a scrollable area containing the form and buttons.
        """
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()

        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(20, 20, 20, 20)

        self.form_layout = QFormLayout()
        self.scroll_layout.addLayout(self.form_layout)

        self.scroll_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.button_layout = QHBoxLayout()
        self.preview_button = QPushButton("Preview")
        self.preview_button.setStyleSheet("background-color: #444444; color: white; padding: 8px 16px; border-radius: 4px;")

        self.apply_button = QPushButton("Apply")
        self.apply_button.setStyleSheet("background-color: #4fc1ff; color: black; font-weight: bold; padding: 8px 16px; border-radius: 4px;")

        self.button_layout.addStretch()
        self.button_layout.addWidget(self.preview_button)
        self.button_layout.addWidget(self.apply_button)

        self.layout.addLayout(self.button_layout)

        self.field_widgets = {}
        self.error_labels = {}

    def add_input_field(self, label_text, widget, field_key=None):
        """
        Adds a labeled widget to the form layout and registers it for error highlighting.
        """
        label = QLabel(label_text)

        if field_key:
            field_container = QWidget()
            field_layout = QVBoxLayout(field_container)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(2)

            field_layout.addWidget(widget)

            error_label = QLabel()
            error_label.setStyleSheet("color: #ff4c4c; font-size: 12px; font-weight: bold; margin-top: 2px;")
            error_label.hide()
            field_layout.addWidget(error_label)

            self.form_layout.addRow(label, field_container)

            self.field_widgets[field_key] = widget
            self.error_labels[field_key] = error_label

            widget.installEventFilter(self)
        else:
            self.form_layout.addRow(label, widget)

    def eventFilter(self, source, event):
        """
        Catches mouse click or focus events on input widgets to clear error highlights.
        """
        if event.type() == QEvent.Type.MouseButtonPress or event.type() == QEvent.Type.FocusIn:
            for field_key, widget in self.field_widgets.items():
                if source is widget:
                    self.clear_field_highlight(field_key)
                    break
        return super().eventFilter(source, event)

    def highlight_errors(self, errors: dict):
        """
        Applies red styling and error messages below specific widgets based on the errors dictionary.
        """
        self.clear_highlights()
        for field, message in errors.items():
            if field in self.error_labels:
                self.error_labels[field].setText(message)
                self.error_labels[field].show()
            if field in self.field_widgets:
                self.field_widgets[field].setStyleSheet("border: 1px solid #ff4c4c; background-color: rgba(255, 76, 76, 0.1);")

    def clear_highlights(self):
        """
        Resets all widgets to their original visual state, removing error messages.
        """
        for error_label in self.error_labels.values():
            error_label.setText("")
            error_label.hide()
        for widget in self.field_widgets.values():
            widget.setStyleSheet("")

    def clear_field_highlight(self, field_key):
        """
        Clears the error highlight for a specific field.
        """
        if field_key in self.error_labels:
            self.error_labels[field_key].setText("")
            self.error_labels[field_key].hide()
        if field_key in self.field_widgets:
            self.field_widgets[field_key].setStyleSheet("")