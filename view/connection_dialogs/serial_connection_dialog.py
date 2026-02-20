import serial.tools.list_ports
from PySide6.QtWidgets import QComboBox, QMessageBox, QLineEdit
from .base_connection_dialog import BaseConnectionDialog

class SerialConnectionDialog(BaseConnectionDialog):
    def __init__(self, parent=None):
        super().__init__("Add Serial Connection", parent)
        self._refresh_com_ports()

    def _add_specific_fields(self):
        self.port_input = QComboBox()
        self.port_input.showPopup = self._refresh_ports_and_show_popup

        self.baud_input = QComboBox()
        self.baud_input.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud_input.setCurrentText("9600")

        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.form.addRow("Serial Port:", self.port_input)
        self.form.addRow("Baud Rate:", self.baud_input)
        self.form.addRow("Console Password:", self.pass_input)

    def _refresh_com_ports(self):
        current_port = self.port_input.currentText()
        self.port_input.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]

        if not ports:
            self.port_input.addItem("No ports found")
            self.port_input.model().item(0).setEnabled(False)
        else:
            self.port_input.addItems(ports)
            if current_port in ports:
                self.port_input.setCurrentText(current_port)

    def _refresh_ports_and_show_popup(self):
        self._refresh_com_ports()
        QComboBox.showPopup(self.port_input)

    def _validate_specific(self):
        port_text = self.port_input.currentText().strip()
        if not port_text or port_text == "No ports found":
            QMessageBox.warning(self, "Error", "A valid Serial Port must be selected.")
            return False
        return True

    def get_data(self):
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