from PySide6.QtWidgets import QComboBox
from model.port_manager import PortManager


class PortComboBox(QComboBox):
    """
    Custom QComboBox that dynamically loads available COM ports upon user interaction.
    """

    def __init__(self, parent=None):
        """
        Initializes the combo box and performs an initial population of available serial ports.
        """
        super().__init__(parent)
        self.refresh_ports()

    def showPopup(self):
        """
        Overrides the default showPopup behavior to refresh the port list dynamically before displaying.
        """
        self.refresh_ports()
        super().showPopup()

    def refresh_ports(self):
        """
        Fetches available serial ports using the PortManager and updates the drop-down items.
        Retains the previously selected port if it is still available in the updated list.
        """
        current_port = self.currentText()
        self.clear()

        ports = PortManager.list_ports()
        for port in ports:
            self.addItem(port.device)

        if current_port:
            index = self.findText(current_port)
            if index >= 0:
                self.setCurrentIndex(index)