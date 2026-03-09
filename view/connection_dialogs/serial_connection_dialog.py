from PySide6.QtWidgets import QComboBox, QMessageBox, QLineEdit
from .base_connection_dialog import BaseConnectionDialog
from view.device_configuration_views.input_fields.port_combobox import PortComboBox

class SerialConnectionDialog(BaseConnectionDialog):
    """
    Dialog for configuring and validating a serial connection utilizing a dynamic port selection component.
    """
    def __init__(self, parent=None):
        """
        Initializes the dialog without requiring manual port refreshing.
        """
        super().__init__("Add Serial Connection", parent)

    def _add_specific_fields(self):
        """
        Injects the customized port combobox alongside standard connection inputs into the form layout.
        """
        self.port_input = PortComboBox()

        self.baud_input = QComboBox()
        self.baud_input.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud_input.setCurrentText("9600")

        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.form.addRow("Serial Port:", self.port_input)
        self.form.addRow("Baud Rate:", self.baud_input)
        self.form.addRow("Console Password:", self.pass_input)

    def _validate_specific(self):
        """
        Validates the serial-specific constraints.
        """
        port_text = self.port_input.currentText().strip()
        if not port_text:
            QMessageBox.warning(self, "Error", "A valid Serial Port must be selected.")
            return False
        return True

    def get_data(self):
        """
        Extracts and formats the provided input data into a structured dictionary.
        """
        return {
            "name": self.name_input.text().strip(),
            "device_type": "cisco_ios_serial",
            "serial_settings": {
                "port": self.port_input.currentText().strip(),
                "baudrate": int(self.baud_input.currentText())
            },
            "password": self.pass_input.text(),
            "secret": self.secret_input.text().strip()
        }