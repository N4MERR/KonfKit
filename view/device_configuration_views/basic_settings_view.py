from PySide6.QtWidgets import QLineEdit, QTextEdit, QCheckBox, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QMessageBox, \
    QSizePolicy
from PySide6.QtCore import Signal, Qt
from view.device_configuration_views.base_config_view import BaseConfigView


class BasicSettingsView(BaseConfigView):
    """
    View providing inputs for Hostname, Enable Secret, and Banner MOTD with toggle checkboxes.
    """
    apply_config_signal = Signal(dict)
    preview_config_signal = Signal(dict)

    def __init__(self):
        """
        Initializes the basic settings form components and connects action buttons to signal handlers.
        """
        super().__init__("Basic Device Configuration")

        self.hostname_input = QLineEdit()
        self.hostname_check = QCheckBox()
        self.hostname_input.textChanged.connect(lambda text: self.hostname_check.setChecked(bool(text)))
        self._add_row_with_toggle("Hostname:", self.hostname_input, self.hostname_check)

        self.secret_input = QLineEdit()
        self.secret_input.setEchoMode(QLineEdit.Password)
        self.secret_check = QCheckBox()
        self.secret_input.textChanged.connect(lambda text: self.secret_check.setChecked(bool(text)))
        self._add_row_with_toggle("Enable Secret:", self.secret_input, self.secret_check)

        self.secret_confirm_input = QLineEdit()
        self.secret_confirm_input.setEchoMode(QLineEdit.Password)
        self.secret_confirm_dummy_check = QCheckBox()

        sp_retain = self.secret_confirm_dummy_check.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.secret_confirm_dummy_check.setSizePolicy(sp_retain)

        self.secret_confirm_dummy_check.setVisible(False)
        self._add_row_with_toggle("Confirm Secret:", self.secret_confirm_input, self.secret_confirm_dummy_check)

        self.encryption_check = QCheckBox("Enable Service Password Encryption")
        self.add_input_field("Encryption:", self.encryption_check)

        self.banner_input = QTextEdit()
        self.banner_input.setMinimumHeight(150)
        self.banner_check = QCheckBox()
        self.banner_input.textChanged.connect(
            lambda: self.banner_check.setChecked(bool(self.banner_input.toPlainText())))

        banner_container = QWidget()
        banner_layout = QVBoxLayout(banner_container)
        banner_layout.setContentsMargins(0, 5, 0, 5)

        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Banner MOTD Content:"))
        header_layout.addStretch()
        header_layout.addWidget(self.banner_check)

        banner_layout.addLayout(header_layout)
        banner_layout.addWidget(self.banner_input)
        self.form_layout.addRow(banner_container)

        self.apply_button.clicked.connect(self._on_apply_clicked)
        self.preview_button.clicked.connect(self._on_preview_clicked)

    def _add_row_with_toggle(self, label_text, input_widget, checkbox):
        """
        Adds a standard input row with a trailing checkbox for enablement.
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(input_widget)
        layout.addWidget(checkbox)
        self.add_input_field(label_text, container)

    def _get_data(self):
        """
        Extracts data from the UI and validates password matching.
        """
        if self.secret_check.isChecked() and self.secret_input.text() != self.secret_confirm_input.text():
            QMessageBox.warning(self, "Validation Error", "Passwords do not match!")
            return None

        return {
            "hostname": self.hostname_input.text(),
            "hostname_enabled": self.hostname_check.isChecked(),
            "secret": self.secret_input.text(),
            "secret_enabled": self.secret_check.isChecked(),
            "encrypt_all": self.encryption_check.isChecked(),
            "banner": self.banner_input.toPlainText(),
            "banner_enabled": self.banner_check.isChecked()
        }

    def _on_apply_clicked(self):
        """
        Triggers the apply signal.
        """
        data = self._get_data()
        if data:
            self.apply_config_signal.emit(data)

    def _on_preview_clicked(self):
        """
        Triggers the preview signal.
        """
        data = self._get_data()
        if data:
            self.preview_config_signal.emit(data)

    def clear_inputs(self):
        """
        Clears all form fields.
        """
        self.hostname_input.clear()
        self.hostname_check.setChecked(False)
        self.secret_input.clear()
        self.secret_confirm_input.clear()
        self.secret_check.setChecked(False)
        self.encryption_check.setChecked(False)
        self.banner_input.clear()
        self.banner_check.setChecked(False)