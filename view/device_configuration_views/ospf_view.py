from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Signal
from view.device_configuration_views.base_config_view import BaseConfigView


class OSPFView(BaseConfigView):
    """
    OSPF-specific user interface view inheriting from BaseConfigView.
    """
    apply_config_signal = Signal(dict)

    def __init__(self):
        """
        Initializes the OSPF view, builds specific input fields, and binds the apply button.
        """
        super().__init__("OSPF Configuration")

        self.process_id_input = QLineEdit()
        self.process_id_input.setPlaceholderText("e.g. 1")
        self.add_input_field("Process ID:", self.process_id_input)

        self.network_input = QLineEdit()
        self.network_input.setPlaceholderText("e.g. 192.168.1.0")
        self.add_input_field("Network:", self.network_input)

        self.wildcard_mask_input = QLineEdit()
        self.wildcard_mask_input.setPlaceholderText("e.g. 0.0.0.255")
        self.add_input_field("Wildcard Mask:", self.wildcard_mask_input)

        self.area_input = QLineEdit()
        self.area_input.setPlaceholderText("e.g. 0")
        self.add_input_field("Area:", self.area_input)

        self.apply_button.clicked.connect(self._on_apply_clicked)

    def _on_apply_clicked(self):
        """
        Packages current inputs into a dictionary and emits the configuration signal.
        """
        data = {
            "process_id": self.process_id_input.text(),
            "network": self.network_input.text(),
            "wildcard_mask": self.wildcard_mask_input.text(),
            "area": self.area_input.text()
        }
        self.apply_config_signal.emit(data)

    def clear_inputs(self):
        """
        Clears all OSPF specific QLineEdit fields.
        """
        self.process_id_input.clear()
        self.network_input.clear()
        self.wildcard_mask_input.clear()
        self.area_input.clear()