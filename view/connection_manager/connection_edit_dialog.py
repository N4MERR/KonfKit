from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox


class ConnectionEditDialog(QDialog):
    """
    Dialog for entering connection details for Serial, SSH, or Telnet sessions.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connection Details")
        self._setup_ui()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.form = QFormLayout()

        self.name_input = QLineEdit()
        self.protocol_input = QComboBox()
        self.protocol_input.addItems(["SSH", "Telnet", "Serial"])

        self.host_input = QLineEdit()
        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.form.addRow("Profile Name:", self.name_input)
        self.form.addRow("Protocol:", self.protocol_input)
        self.form.addRow("Host/Port:", self.host_input)
        self.form.addRow("Username:", self.user_input)
        self.form.addRow("Password:", self.pass_input)

        self.layout.addLayout(self.form)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "protocol": self.protocol_input.currentText(),
            "host": self.host_input.text(),
            "username": self.user_input.text(),
            "password": self.pass_input.text()
        }