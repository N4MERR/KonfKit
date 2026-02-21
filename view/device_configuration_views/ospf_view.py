from PySide6.QtWidgets import QLineEdit, QMessageBox, QCheckBox
from PySide6.QtCore import Signal
from view.device_configuration_views.base_config_view import BaseConfigView
from utils.input_validator import InputValidator

class OSPFBasicView(BaseConfigView):
    """
    OSPF basic network configuration view inheriting from BaseConfigView.
    """
    apply_config_signal = Signal(dict)

    def __init__(self):
        """
        Initializes the OSPF basic view, builds specific input fields, and binds the apply button.
        """
        super().__init__("OSPF Basic Configuration")

        self.process_id_input = QLineEdit()
        self.add_input_field("Process ID:", self.process_id_input)

        self.network_input = QLineEdit()
        self.add_input_field("Network:", self.network_input)

        self.wildcard_mask_input = QLineEdit()
        self.add_input_field("Wildcard Mask:", self.wildcard_mask_input)

        self.area_input = QLineEdit()
        self.add_input_field("Area:", self.area_input)

        self.apply_button.clicked.connect(self._on_apply_clicked)

    def _on_apply_clicked(self):
        """
        Validates inputs using the InputValidator utility, reports specific errors, and emits the data.
        """
        missing_fields = []
        if not self.process_id_input.text().strip():
            missing_fields.append("Process ID")
        if not self.network_input.text().strip():
            missing_fields.append("Network")
        if not self.wildcard_mask_input.text().strip():
            missing_fields.append("Wildcard Mask")
        if not self.area_input.text().strip():
            missing_fields.append("Area")

        if missing_fields:
            QMessageBox.warning(self, "Validation Error", f"The following required fields are missing:\n{', '.join(missing_fields)}")
            return

        if not InputValidator.is_valid_number(self.process_id_input.text().strip()):
            QMessageBox.warning(self, "Validation Error", "Process ID must be a valid number.")
            return

        if not InputValidator.is_valid_ip(self.network_input.text().strip()):
            QMessageBox.warning(self, "Validation Error", "Network must be a valid IP address format.")
            return

        if not InputValidator.is_valid_wildcard_mask(self.wildcard_mask_input.text().strip()):
            QMessageBox.warning(self, "Validation Error", "Wildcard Mask is invalid. It must be a contiguous wildcard mask.")
            return

        if not InputValidator.is_valid_number(self.area_input.text().strip()):
            QMessageBox.warning(self, "Validation Error", "Area must be a valid number.")
            return

        data = {
            "type": "basic",
            "process_id": self.process_id_input.text().strip(),
            "network": self.network_input.text().strip(),
            "wildcard_mask": self.wildcard_mask_input.text().strip(),
            "area": self.area_input.text().strip()
        }
        self.apply_config_signal.emit(data)

    def clear_inputs(self):
        """
        Clears all OSPF basic QLineEdit fields.
        """
        self.process_id_input.clear()
        self.network_input.clear()
        self.wildcard_mask_input.clear()
        self.area_input.clear()

class OSPFRouterIdView(BaseConfigView):
    """
    OSPF router ID configuration view inheriting from BaseConfigView.
    """
    apply_config_signal = Signal(dict)

    def __init__(self):
        """
        Initializes the OSPF router ID view, builds input fields, and binds the apply button.
        """
        super().__init__("OSPF Router ID Configuration")

        self.process_id_input = QLineEdit()
        self.add_input_field("Process ID:", self.process_id_input)

        self.router_id_input = QLineEdit()
        self.add_input_field("Router ID:", self.router_id_input)

        self.apply_button.clicked.connect(self._on_apply_clicked)

    def _on_apply_clicked(self):
        """
        Validates inputs and emits the configuration data.
        """
        missing_fields = []
        if not self.process_id_input.text().strip():
            missing_fields.append("Process ID")
        if not self.router_id_input.text().strip():
            missing_fields.append("Router ID")

        if missing_fields:
            QMessageBox.warning(self, "Validation Error", f"The following required fields are missing:\n{', '.join(missing_fields)}")
            return

        if not InputValidator.is_valid_number(self.process_id_input.text().strip()):
            QMessageBox.warning(self, "Validation Error", "Process ID must be a valid number.")
            return

        if not InputValidator.is_valid_ip(self.router_id_input.text().strip()):
            QMessageBox.warning(self, "Validation Error", "Router ID must be a valid IP address format.")
            return

        data = {
            "type": "router_id",
            "process_id": self.process_id_input.text().strip(),
            "router_id": self.router_id_input.text().strip()
        }
        self.apply_config_signal.emit(data)

    def clear_inputs(self):
        """
        Clears all input fields.
        """
        self.process_id_input.clear()
        self.router_id_input.clear()

class OSPFPassiveInterfaceView(BaseConfigView):
    """
    OSPF passive interface configuration view inheriting from BaseConfigView.
    """
    apply_config_signal = Signal(dict)

    def __init__(self):
        """
        Initializes the OSPF passive interface view, builds input fields, and binds the apply button.
        """
        super().__init__("OSPF Passive Interface Configuration")

        self.process_id_input = QLineEdit()
        self.add_input_field("Process ID:", self.process_id_input)

        self.interface_input = QLineEdit()
        self.add_input_field("Interface Name:", self.interface_input)

        self.apply_button.clicked.connect(self._on_apply_clicked)

    def _on_apply_clicked(self):
        """
        Validates inputs and emits the configuration data.
        """
        missing_fields = []
        if not self.process_id_input.text().strip():
            missing_fields.append("Process ID")
        if not self.interface_input.text().strip():
            missing_fields.append("Interface Name")

        if missing_fields:
            QMessageBox.warning(self, "Validation Error", f"The following required fields are missing:\n{', '.join(missing_fields)}")
            return

        if not InputValidator.is_valid_number(self.process_id_input.text().strip()):
            QMessageBox.warning(self, "Validation Error", "Process ID must be a valid number.")
            return

        data = {
            "type": "passive_interface",
            "process_id": self.process_id_input.text().strip(),
            "interface_name": self.interface_input.text().strip()
        }
        self.apply_config_signal.emit(data)

    def clear_inputs(self):
        """
        Clears all input fields.
        """
        self.process_id_input.clear()
        self.interface_input.clear()

class OSPFDefaultRouteView(BaseConfigView):
    """
    OSPF default route advertisement view inheriting from BaseConfigView.
    """
    apply_config_signal = Signal(dict)

    def __init__(self):
        """
        Initializes the OSPF default route view, builds input fields, and binds the apply button.
        """
        super().__init__("OSPF Default Route Advertisement")

        self.process_id_input = QLineEdit()
        self.add_input_field("Process ID:", self.process_id_input)

        self.always_checkbox = QCheckBox("Always originate")
        self.add_input_field("Options:", self.always_checkbox)

        self.apply_button.clicked.connect(self._on_apply_clicked)

    def _on_apply_clicked(self):
        """
        Validates inputs and emits the configuration data.
        """
        if not self.process_id_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "The Process ID field is missing.")
            return

        if not InputValidator.is_valid_number(self.process_id_input.text().strip()):
            QMessageBox.warning(self, "Validation Error", "Process ID must be a valid number.")
            return

        data = {
            "type": "default_route",
            "process_id": self.process_id_input.text().strip(),
            "always": self.always_checkbox.isChecked()
        }
        self.apply_config_signal.emit(data)

    def clear_inputs(self):
        """
        Clears all input fields.
        """
        self.process_id_input.clear()
        self.always_checkbox.setChecked(False)