from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QHBoxLayout, \
    QMessageBox, QLabel
from PySide6.QtCore import Signal
from model.port_manager import PortManager


class PortComboBox(QComboBox):
    """
    A specialized ComboBox that refreshes available serial ports and notifies if empty.
    """

    def __init__(self, status_label, parent=None):
        super().__init__(parent)
        self.status_label = status_label

    def showPopup(self):
        self.clear()
        ports = [p.device for p in PortManager.list_ports()]
        if not ports:
            self.status_label.setText("No valid ports found")
            self.status_label.show()
        else:
            self.status_label.hide()
            self.addItems(ports)
        super().showPopup()


class SerialConnectionDialog(QDialog):
    """
    Serial configuration dialog with threaded hardware port testing requests.
    """
    test_requested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Serial Connection")
        self.setMinimumWidth(450)
        self._setup_ui()

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.form = QFormLayout()
        self.form.setSpacing(10)

        self.name_input = QLineEdit()
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #ff4d4d; font-weight: bold;")
        self.status_label.hide()
        self.port_input = PortComboBox(self.status_label)

        self.baud_input = QComboBox()
        self.baud_input.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud_input.setCurrentText("9600")

        self.form.addRow("Profile Name:", self.name_input)
        self.form.addRow(self.status_label)
        self.form.addRow("Serial Port:", self.port_input)
        self.form.addRow("Baud Rate:", self.baud_input)
        self.layout.addLayout(self.form)

        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self._on_test_clicked)
        self.layout.addWidget(self.test_btn)

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
        self.layout.addLayout(self.button_layout)

    def _on_test_clicked(self):
        if self.name_input.text().strip() and self.port_input.currentText():
            self.test_requested.emit(self.get_data())
        else:
            QMessageBox.warning(self, "Error", "Name and Port are required.")

    def handle_save(self):
        if self.name_input.text().strip():
            self.done(10)
        else:
            QMessageBox.warning(self, "Error", "Name is required.")

    def handle_connect(self):
        if self.name_input.text().strip() and self.port_input.currentText():
            self.done(20)
        else:
            QMessageBox.warning(self, "Error", "Name and Port are required.")

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "protocol": "Serial",
            "host": self.port_input.currentText(),
            "baud": int(self.baud_input.currentText())
        }