import re
from PySide6.QtWidgets import QLineEdit, QMessageBox
from .base_connection_dialog import BaseConnectionDialog

class TelnetConnectionDialog(BaseConnectionDialog):
    def __init__(self, parent=None):
        super().__init__("Add Telnet Connection", parent)

    def _add_specific_fields(self):
        self.ip_input = QLineEdit()
        self.port_input = QLineEdit("23")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.form.addRow("IP Address:", self.ip_input)
        self.form.addRow("Telnet Port:", self.port_input)
        self.form.addRow("Password:", self.pass_input)

    def is_valid_ip(self, ip):
        pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        if not re.match(pattern, ip):
            return False
        return all(0 <= int(part) <= 255 for part in ip.split('.'))

    def _validate_specific(self):
        if not self.is_valid_ip(self.ip_input.text().strip()):
            QMessageBox.warning(self, "Error", "Valid IP Address is required.")
            return False
        return True

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "device_type": "cisco_ios_telnet",
            "host": self.ip_input.text().strip(),
            "port": int(self.port_input.text() or 23),
            "password": self.pass_input.text(),
            "secret": self.secret_input.text().strip()
        }