from PySide6.QtWidgets import QLineEdit, QCheckBox
from PySide6.QtCore import Signal
from view.device_configuration_views.base_config_view import BaseConfigView

class OSPFBasicView(BaseConfigView):
    """
    View for OSPF network configuration with highlighted validation fields.
    """
    apply_config_signal = Signal(dict)
    preview_config_signal = Signal(dict)

    def __init__(self):
        """
        Initializes the basic OSPF form and registers fields for error highlighting.
        """
        super().__init__("OSPF Basic Configuration")
        self.process_id_input = QLineEdit()
        self.add_input_field("Process ID:", self.process_id_input, "process_id")
        self.network_input = QLineEdit()
        self.add_input_field("Network:", self.network_input, "network")
        self.wildcard_mask_input = QLineEdit()
        self.add_input_field("Wildcard Mask:", self.wildcard_mask_input, "wildcard_mask")
        self.area_input = QLineEdit()
        self.add_input_field("Area:", self.area_input, "area")

        self.preview_button.clicked.connect(lambda: self.preview_config_signal.emit(self._get_data()))
        self.apply_button.clicked.connect(lambda: self.apply_config_signal.emit(self._get_data()))

    def _get_data(self) -> dict:
        """
        Extracts OSPF basic configuration data from the UI.
        """
        return {
            "type": "basic",
            "process_id": self.process_id_input.text().strip(),
            "network": self.network_input.text().strip(),
            "wildcard_mask": self.wildcard_mask_input.text().strip(),
            "area": self.area_input.text().strip()
        }

class OSPFRouterIdView(BaseConfigView):
    """
    View for OSPF Router ID configuration.
    """
    apply_config_signal = Signal(dict)
    preview_config_signal = Signal(dict)

    def __init__(self):
        """
        Initializes the Router ID form.
        """
        super().__init__("OSPF Router ID Configuration")
        self.process_id_input = QLineEdit()
        self.add_input_field("Process ID:", self.process_id_input, "process_id")
        self.router_id_input = QLineEdit()
        self.add_input_field("Router ID:", self.router_id_input, "router_id")

        self.preview_button.clicked.connect(lambda: self.preview_config_signal.emit(self._get_data()))
        self.apply_button.clicked.connect(lambda: self.apply_config_signal.emit(self._get_data()))

    def _get_data(self) -> dict:
        """
        Extracts Router ID data from the UI.
        """
        return {
            "type": "router_id",
            "process_id": self.process_id_input.text().strip(),
            "router_id": self.router_id_input.text().strip()
        }

class OSPFPassiveInterfaceView(BaseConfigView):
    """
    View for OSPF Passive Interface configuration.
    """
    apply_config_signal = Signal(dict)
    preview_config_signal = Signal(dict)

    def __init__(self):
        """
        Initializes the Passive Interface form.
        """
        super().__init__("OSPF Passive Interface Configuration")
        self.process_id_input = QLineEdit()
        self.add_input_field("Process ID:", self.process_id_input, "process_id")
        self.interface_input = QLineEdit()
        self.add_input_field("Interface Name:", self.interface_input, "interface_name")

        self.preview_button.clicked.connect(lambda: self.preview_config_signal.emit(self._get_data()))
        self.apply_button.clicked.connect(lambda: self.apply_config_signal.emit(self._get_data()))

    def _get_data(self) -> dict:
        """
        Extracts Passive Interface data from the UI.
        """
        return {
            "type": "passive_interface",
            "process_id": self.process_id_input.text().strip(),
            "interface_name": self.interface_input.text().strip()
        }

class OSPFDefaultRouteView(BaseConfigView):
    """
    View for OSPF Default Route Advertisement.
    """
    apply_config_signal = Signal(dict)
    preview_config_signal = Signal(dict)

    def __init__(self):
        """
        Initializes the Default Route form.
        """
        super().__init__("OSPF Default Route Advertisement")
        self.process_id_input = QLineEdit()
        self.add_input_field("Process ID:", self.process_id_input, "process_id")
        self.always_checkbox = QCheckBox("Always originate")
        self.add_input_field("Options:", self.always_checkbox)

        self.preview_button.clicked.connect(lambda: self.preview_config_signal.emit(self._get_data()))
        self.apply_button.clicked.connect(lambda: self.apply_config_signal.emit(self._get_data()))

    def _get_data(self) -> dict:
        """
        Extracts Default Route data from the UI.
        """
        return {
            "type": "default_route",
            "process_id": self.process_id_input.text().strip(),
            "always": self.always_checkbox.isChecked()
        }