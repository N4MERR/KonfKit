from PySide6.QtWidgets import QLineEdit
from view.connection_dialogs.base_connection_dialog import BaseConnectionDialog


class SSHConnectionDialog(BaseConnectionDialog):
    """
    Dialog specifically for creating and editing SSH connection profiles.
    """

    def __init__(self, parent=None, profile_data=None):
        """
        Initializes the SSH connection dialog.
        """
        super().__init__(parent, profile_data, "SSH")

    def _setup_specific_fields(self):
        """
        Adds SSH-specific fields including username, password, and enable secret.
        """
        self.username_input = QLineEdit()
        if self.profile_data:
            self.username_input.setText(self.profile_data.get("username", ""))
        self.form_layout.addRow("Username:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        if self.profile_data:
            self.password_input.setText(self.profile_data.get("password", ""))
        self.form_layout.addRow("Password:", self.password_input)

        self.secret_input = QLineEdit()
        self.secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        if self.profile_data:
            self.secret_input.setText(self.profile_data.get("secret", ""))
        self.form_layout.addRow("Enable Secret:", self.secret_input)

    def get_connection_data(self):
        """
        Retrieves the configured SSH connection parameters without background keepalives.
        """
        data = super().get_connection_data()
        data.update({
            "username": self.username_input.text().strip(),
            "password": self.password_input.text(),
            "secret": self.secret_input.text(),
            "device_type": "cisco_ios",
        })
        return data