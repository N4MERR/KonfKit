from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QWidget
from PySide6.QtCore import Signal

class BaseConnectionDialog(QDialog):
    test_requested = Signal(dict)

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(450)
        self._setup_base_ui()

    def _setup_base_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)

        self.form = QFormLayout()
        self.form.setSpacing(10)
        self.name_input = QLineEdit()
        self.form.addRow("Profile Name:", self.name_input)

        self._add_specific_fields()

        self.secret_input = QLineEdit()
        self.secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.form.addRow("Secret:", self.secret_input)
        self.content_layout.addLayout(self.form)

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

    def _add_specific_fields(self):
        pass

    def _on_test_clicked(self):
        if self.validate_inputs(require_name=False):
            self.test_requested.emit(self.get_data())

    def validate_inputs(self, require_name=True):
        if require_name and not self.name_input.text().strip():
            QMessageBox.warning(self, "Error", "Profile Name is required for saving.")
            return False
        return self._validate_specific()

    def _validate_specific(self):
        return True

    def handle_save(self):
        if self.validate_inputs(require_name=True):
            self.done(10)

    def handle_connect(self):
        if self.validate_inputs(require_name=False):
            self.done(20)

    def get_data(self):
        return {}