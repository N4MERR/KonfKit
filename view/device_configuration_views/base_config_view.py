from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFormLayout, QPushButton
from PySide6.QtCore import Qt

class BaseConfigView(QWidget):
    """
    Base view class establishing the standard layout and UI components for configuration tabs.
    """

    def __init__(self, title: str):
        """
        Initializes the base UI layout, title, form structure, and action buttons.
        """
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.layout.addLayout(self.form_layout)
        self.layout.addStretch()

        self.button_layout = QHBoxLayout()
        self.preview_button = QPushButton("Preview Configuration")
        self.apply_button = QPushButton("Apply Configuration")
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.preview_button)
        self.button_layout.addWidget(self.apply_button)

        self.layout.addLayout(self.button_layout)

    def add_input_field(self, label: str, widget: QWidget):
        """
        Adds a labeled input widget to the form layout.
        """
        self.form_layout.addRow(label, widget)

    def clear_inputs(self):
        """
        Must be implemented by child classes to define how inputs are cleared.
        """
        raise NotImplementedError