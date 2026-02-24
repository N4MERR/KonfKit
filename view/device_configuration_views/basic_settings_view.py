"""
Provides the view for configuring basic device settings like hostname, secret, and banner.
"""
from PySide6.QtWidgets import QLineEdit, QTextEdit, QCheckBox, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QSizePolicy, QPushButton
from PySide6.QtCore import Signal, Qt
from view.device_configuration_views.base_config_view import BaseConfigView


class BasicSettingsView(BaseConfigView):
    """
    View for basic device configuration including Hostname, Enable Secret, and Banner MOTD.
    """
    apply_config_signal = Signal(dict)
    preview_config_signal = Signal(dict)

    def __init__(self):
        """
        Initializes basic setting inputs and registers them with the base class for validation highlighting.
        """
        super().__init__()

        self.hostname_input = QLineEdit()
        self.hostname_check = QCheckBox()
        self.hostname_input.textChanged.connect(lambda text: self.hostname_check.setChecked(bool(text)))
        self.hostname_input.textChanged.connect(lambda: self.clear_field_highlight("hostname"))
        self._add_row_with_toggle("Hostname:", self.hostname_input, self.hostname_check, "hostname")

        self.secret_input = QLineEdit()
        self.secret_input.setEchoMode(QLineEdit.Password)
        self.secret_check = QCheckBox()
        self.secret_input.textChanged.connect(lambda text: self.secret_check.setChecked(bool(text)))
        self.secret_input.textChanged.connect(lambda: self.clear_field_highlight("secret"))
        self._add_row_with_toggle("Enable Secret:", self.secret_input, self.secret_check, "secret", is_password=True)

        self.secret_confirm_input = QLineEdit()
        self.secret_confirm_input.setEchoMode(QLineEdit.Password)
        self.secret_confirm_input.textChanged.connect(lambda: self.clear_field_highlight("confirm"))

        dummy_check = QCheckBox()
        policy = dummy_check.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        dummy_check.setSizePolicy(policy)
        dummy_check.hide()

        self._add_row_with_toggle("Confirm Secret:", self.secret_confirm_input, dummy_check, "confirm", is_password=True)

        self.encryption_check = QCheckBox("Enable Service Password Encryption")
        self.add_input_field("Encryption:", self.encryption_check)

        self.banner_input = QTextEdit()
        self.banner_input.setMinimumHeight(150)
        self.banner_check = QCheckBox()
        self.banner_input.textChanged.connect(
            lambda: self.banner_check.setChecked(bool(self.banner_input.toPlainText())))

        banner_container = QWidget()
        banner_layout = QVBoxLayout(banner_container)
        banner_layout.setContentsMargins(0, 0, 0, 0)

        header_layout = QHBoxLayout()
        header_label = QLabel("Banner MOTD:")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(self.banner_check)

        banner_layout.addLayout(header_layout)
        banner_layout.addWidget(self.banner_input)

        error_label = QLabel()
        error_label.setStyleSheet("color: #ff4c4c; font-size: 12px; font-weight: bold; margin-top: 2px;")
        error_label.hide()
        banner_layout.addWidget(error_label)

        self.form_layout.addRow(banner_container)
        self.field_widgets["banner"] = self.banner_input
        self.error_labels["banner"] = error_label
        self.banner_input.installEventFilter(self)

        self.apply_button.clicked.connect(self._on_apply_clicked)
        self.preview_button.clicked.connect(self._on_preview_clicked)

    def _add_row_with_toggle(self, label_text, input_widget, checkbox, key, is_password=False):
        """
        Creates a layout for a text input with an optional trailing checkbox and an inline password visibility toggle.
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(input_widget)

        if is_password:
            toggle_btn = QPushButton("Show", input_widget)
            toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            toggle_btn.setCheckable(True)
            toggle_btn.setStyleSheet("QPushButton { border: none; background: transparent; color: #a0a0a0; font-size: 11px; font-weight: bold; padding: 0px 5px; } QPushButton:checked { color: #4fc1ff; }")

            toggle_btn.toggled.connect(lambda checked, btn=toggle_btn, w=input_widget: (
                w.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password),
                btn.setText("Hide" if checked else "Show")
            ))

            inner_layout = QHBoxLayout(input_widget)
            inner_layout.setContentsMargins(0, 0, 2, 0)
            inner_layout.addStretch()
            inner_layout.addWidget(toggle_btn)

            input_widget.setTextMargins(0, 0, 35, 0)

        if checkbox:
            layout.addWidget(checkbox)

        self.add_input_field(label_text, container, key)
        self.field_widgets[key] = input_widget
        input_widget.installEventFilter(self)

    def _get_data(self):
        """
        Gathers all user input data from the form into a dictionary for processing.
        """
        return {
            "hostname": self.hostname_input.text(),
            "hostname_enabled": self.hostname_check.isChecked(),
            "secret": self.secret_input.text(),
            "secret_enabled": self.secret_check.isChecked(),
            "confirm_secret": self.secret_confirm_input.text(),
            "encrypt_all": self.encryption_check.isChecked(),
            "banner": self.banner_input.toPlainText(),
            "banner_enabled": self.banner_check.isChecked()
        }

    def _on_apply_clicked(self):
        """
        Clears previous highlights and emits the apply signal with form data.
        """
        self.clear_highlights()
        self.apply_config_signal.emit(self._get_data())

    def _on_preview_clicked(self):
        """
        Clears previous highlights and emits the preview signal with form data.
        """
        self.clear_highlights()
        self.preview_config_signal.emit(self._get_data())