"""
Provides the view for configuring Telnet settings.
"""
from PySide6.QtWidgets import QLineEdit, QCheckBox, QHBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Signal, Qt
from view.device_configuration_views.base_config_view import BaseConfigView


class TelnetView(BaseConfigView):
    """
    View for configuring Telnet device management.
    """
    apply_config_signal = Signal(dict)
    preview_config_signal = Signal(dict)

    def __init__(self):
        """
        Initializes the inputs for Telnet VTY lines and login credentials.
        """
        super().__init__()

        self.vty_start = QLineEdit("0")
        self.vty_end = QLineEdit("4")
        vty_layout = QHBoxLayout()
        vty_layout.setContentsMargins(0, 0, 0, 0)
        vty_layout.addWidget(self.vty_start)
        vty_layout.addWidget(self.vty_end)
        vty_container = QWidget()
        vty_container.setLayout(vty_layout)
        self.add_input_field("VTY Lines (Start - End):", vty_container, "vty")

        self.local_login_check = QCheckBox("Use Local Login")
        self.local_login_check.setChecked(True)
        self.add_input_field("Login Method:", self.local_login_check, "login")

        self.username_input = QLineEdit()
        self.add_input_field("Admin Username:", self.username_input, "username")

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.toggle_btn = QPushButton("Show", self.password_input)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; color: #a0a0a0; font-size: 11px; font-weight: bold; padding: 0px 5px; } QPushButton:checked { color: #4fc1ff; }")

        self.toggle_btn.toggled.connect(lambda checked: (
            self.password_input.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password),
            self.toggle_btn.setText("Hide" if checked else "Show")
        ))

        inner_layout = QHBoxLayout(self.password_input)
        inner_layout.setContentsMargins(0, 0, 2, 0)
        inner_layout.addStretch()
        inner_layout.addWidget(self.toggle_btn)

        self.password_input.setTextMargins(0, 0, 35, 0)

        self.add_input_field("Admin Password:", self.password_input, "password")

        self.vty_start.installEventFilter(self)
        self.vty_end.installEventFilter(self)
        self.username_input.installEventFilter(self)
        self.password_input.installEventFilter(self)

        self.apply_button.clicked.connect(self._on_apply_clicked)
        self.preview_button.clicked.connect(self._on_preview_clicked)

    def _get_data(self):
        """
        Gathers all user input data from the form into a dictionary.
        """
        return {
            "vty_start": self.vty_start.text(),
            "vty_end": self.vty_end.text(),
            "local_login": self.local_login_check.isChecked(),
            "username": self.username_input.text(),
            "password": self.password_input.text()
        }

    def _on_apply_clicked(self):
        """
        Clears previous highlights and emits the apply signal.
        """
        self.clear_highlights()
        self.apply_config_signal.emit(self._get_data())

    def _on_preview_clicked(self):
        """
        Clears previous highlights and emits the preview signal.
        """
        self.clear_highlights()
        self.preview_config_signal.emit(self._get_data())