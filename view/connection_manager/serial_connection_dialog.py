import serial.tools.list_ports
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                               QPushButton, QHBoxLayout, QMessageBox, QComboBox, QWidget)
from PySide6.QtCore import Signal, Qt


class SerialConnectionDialog(QDialog):
    """
    Dialog for Serial configuration featuring a dynamic COM port selector with empty state handling.
    """
    test_requested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Serial Connection")
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)

        self.form = QFormLayout()
        self.form.setSpacing(10)
        self.name_input = QLineEdit()

        self.port_input = QComboBox()
        self.port_input.showPopup = self._refresh_ports_and_show_popup

        self.baud_input = QComboBox()
        self.baud_input.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud_input.setCurrentText("9600")

        self.form.addRow("Profile Name:", self.name_input)
        self.form.addRow("Serial Port:", self.port_input)
        self.form.addRow("Baud Rate:", self.baud_input)
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
        self._refresh_com_ports()

    def _refresh_com_ports(self):
        """
        Scans the system for active COM ports and updates the selector. Shows a message if none are found.
        """
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
        """
        Re-scans ports immediately when the user clicks the dropdown.
        """
        self._refresh_com_ports()
        QComboBox.showPopup(self.port_input)

    def _on_test_clicked(self):
        """
        Emits signal with data for hardware testing.
        """
        if self.validate_inputs(require_name=False):
            self.test_requested.emit(self.get_data())

    def validate_inputs(self, require_name=True):
        """
        Ensures name and a valid port are specified.
        """
        if require_name and not self.name_input.text().strip():
            QMessageBox.warning(self, "Error", "Profile Name is required for saving.")
            return False

        port_text = self.port_input.currentText().strip()
        if not port_text or port_text == "No ports found":
            QMessageBox.warning(self, "Error", "A valid Serial Port must be selected.")
            return False

        return True

    def handle_save(self):
        if self.validate_inputs(require_name=True):
            self.done(10)

    def handle_connect(self):
        if self.validate_inputs(require_name=False):
            self.done(20)

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "protocol": "Serial",
            "host": self.port_input.currentText().strip(),
            "baud": int(self.baud_input.currentText())
        }