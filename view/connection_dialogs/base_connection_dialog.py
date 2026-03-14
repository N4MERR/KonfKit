from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QWidget, QLayout
from PySide6.QtCore import Signal
from view.device_configuration_views.input_fields.base_input_field import BaseInputField


class BaseConnectionDialog(QDialog):
    """
    Base dialog for connection profiles utilizing custom input fields for inline validation.
    Dynamically resizes to match the visibility of its layout components.
    """
    test_requested = Signal(dict)

    def __init__(self, title, parent=None):
        """
        Initializes the base connection dialog with a dynamic field list.
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.fields = []
        self._setup_base_ui()

    def _setup_base_ui(self):
        """
        Constructs the dialog layout, injecting specific fields before action buttons,
        and enforces a fixed size constraint to automatically resize the window.
        """
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        self.content_widget = QWidget()
        self.content_widget.setMinimumWidth(450)
        self.content_layout = QVBoxLayout(self.content_widget)

        self.name_input = BaseInputField("Profile Name:", is_optional=False)
        self.name_input.set_error_message("Profile Name is required.")
        self.add_field(self.name_input)

        self._add_specific_fields()

        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self._on_test_clicked)
        self.content_layout.addWidget(self.test_btn)

        self.button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.connect_btn = QPushButton("Connect")
        self.cancel_btn = QPushButton("Cancel")

        self.save_btn.clicked.connect(self.handle_save)
        self.connect_btn.clicked.connect(self.handle_connect)
        self.cancel_btn.clicked.connect(self.reject)

        self.button_layout.addWidget(self.save_btn)
        self.button_layout.addWidget(self.connect_btn)
        self.button_layout.addWidget(self.cancel_btn)
        self.content_layout.addLayout(self.button_layout)

        self.main_layout.addWidget(self.content_widget)

    def add_field(self, field):
        """
        Registers and appends an input field to the layout for validation tracking.
        """
        self.fields.append(field)
        self.content_layout.addWidget(field)

    def _add_specific_fields(self):
        """
        Placeholder for subclasses to inject their specific input fields.
        """
        pass

    def _on_test_clicked(self):
        """
        Validates inputs excluding the profile name before emitting the test signal.
        """
        if self.validate_inputs(require_name=False):
            self.test_requested.emit(self.get_data())

    def validate_inputs(self, require_name=True):
        """
        Iterates through all registered fields and triggers their inline validation.
        Skips hidden fields to prevent invisible validation failures.
        """
        is_valid = True
        for field in self.fields:
            if not require_name and field == self.name_input:
                continue
            if not field.isVisible():
                continue
            if not field.validate():
                is_valid = False
        return is_valid

    def handle_save(self):
        """
        Validates all inputs including the profile name before confirming the dialog.
        """
        if self.validate_inputs(require_name=True):
            self.done(10)

    def handle_connect(self):
        """
        Validates necessary inputs excluding profile name to proceed with connection.
        """
        if self.validate_inputs(require_name=False):
            self.done(20)

    def get_data(self):
        """
        Retrieves collected field data as a dictionary. To be overridden by subclasses.
        """
        return {}