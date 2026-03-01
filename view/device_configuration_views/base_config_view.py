from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal


class BaseConfigView(QWidget):
    """
    Base view for all device configuration tabs.
    """
    preview_config_signal = Signal(dict)
    apply_config_signal = Signal(dict)

    def __init__(self):
        """
        Initializes the base configuration view layout without scroll areas.
        """
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

        self.setStyleSheet(
            "QLabel { background: transparent; }"
            "QCheckBox { background: transparent; }"
        )

        self.form_layout = QVBoxLayout()
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(15)

        self.main_layout.addLayout(self.form_layout)

        self.button_layout = QHBoxLayout()
        self.preview_button = QPushButton("Preview")
        self.apply_button = QPushButton("Apply")
        self.apply_button.setStyleSheet("font-weight: bold;")

        self.button_layout.addStretch()
        self.button_layout.addWidget(self.preview_button)
        self.button_layout.addWidget(self.apply_button)

        self.fields = {}
        self.form_layout.addStretch(1)

        self.main_layout.addLayout(self.button_layout)

        self.preview_button.clicked.connect(self._on_preview_clicked)
        self.apply_button.clicked.connect(self._on_apply_clicked)

    def add_field(self, key, field_widget):
        """
        Registers a field to the view.
        """
        self.fields[key] = field_widget
        self.form_layout.insertWidget(self.form_layout.count() - 1, field_widget)
        return field_widget

    def clear_all_fields(self):
        """
        Resets all registered input fields.
        """
        for field in self.fields.values():
            if hasattr(field, 'reset'):
                field.reset()

    def get_data(self):
        """
        Returns data for active checkboxes or radios.
        """
        if not self.fields:
            return {}

        first_field = next(iter(self.fields.values()))
        if hasattr(first_field, 'checkbox'):
            return {k: f.get_value() for k, f in self.fields.items() if f.checkbox.isChecked()}
        elif hasattr(first_field, 'radio'):
            return {k: f.get_value() for k, f in self.fields.items() if f.radio.isChecked()}
        else:
            return {k: f.get_value() for k, f in self.fields.items()}

    def validate_all(self):
        """
        Validates every field in the view.
        """
        is_valid = True
        for field in self.fields.values():
            if hasattr(field, 'validate') and not field.validate():
                is_valid = False
        return is_valid

    def _on_preview_clicked(self):
        """
        Emits preview signal if valid.
        """
        if self.validate_all():
            self.preview_config_signal.emit(self.get_data())

    def _on_apply_clicked(self):
        """
        Emits apply signal if valid.
        """
        if self.validate_all():
            self.apply_config_signal.emit(self.get_data())