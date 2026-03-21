from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal
from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.input_fields.adaptive_ip_address_field import AdaptiveIPAddressField
from view.device_configuration_views.input_fields.adaptive_subnet_mask_field import AdaptiveSubnetMaskField
from view.device_configuration_views.input_fields.dropdown_field import DropdownField
from utils.input_validator import InputValidator


class StaticRoutingView(BaseConfigView):
    """
    View handling dual-stack router static routing configuration with dynamic next hop selection.
    """
    load_interfaces_signal = Signal()

    def __init__(self):
        """
        Initializes the static routing view with dynamic fields for IP version and next hop type.
        """
        super().__init__()

        self.load_interfaces_btn = QPushButton("Load Interfaces")
        self.load_interfaces_btn.setStyleSheet(
            "QPushButton { background-color: #cccccc; color: black; border: 1px solid #8a8886; border-radius: 4px; padding: 6px; font-weight: bold; }"
            "QPushButton:hover { background-color: #b3b3b3; }"
            "QPushButton:disabled { background-color: #e6e6e6; color: #a0a0a0; border: 1px solid #c0c0c0; }"
        )
        self.load_interfaces_btn.clicked.connect(self.load_interfaces_signal.emit)
        self.button_layout.insertWidget(0, self.load_interfaces_btn)

        self.add_field("network", AdaptiveIPAddressField("Network IP:", is_optional=False))
        self.add_field("mask", AdaptiveSubnetMaskField("Subnet Mask / Prefix:", is_optional=False))

        self.next_hop_type_field = DropdownField("Next Hop Type:", ["IP Address", "Interface"], is_optional=False)
        self.add_field("next_hop_type", self.next_hop_type_field)

        self.next_hop_ip_field = AdaptiveIPAddressField("Next Hop IP:", is_optional=False)
        self.add_field("next_hop_ip", self.next_hop_ip_field)

        self.next_hop_interface_field = DropdownField("Next Hop Interface:", [], is_optional=False)
        self.add_field("next_hop_interface", self.next_hop_interface_field)

        self.next_hop_type_field.input_widget.currentTextChanged.connect(self.toggle_next_hop_fields)
        self.toggle_next_hop_fields(self.next_hop_type_field.get_value())

    def toggle_next_hop_fields(self, selected_type: str):
        """
        Toggles the visibility and validation requirements of IP and Interface fields based on the selected type.
        """
        if selected_type == "IP Address":
            self.next_hop_ip_field.show()
            self.next_hop_ip_field.is_optional = False

            self.next_hop_interface_field.hide()
            self.next_hop_interface_field.is_optional = True
            if hasattr(self.next_hop_interface_field, 'error_label'):
                self.next_hop_interface_field.error_label.setText("")
        else:
            self.next_hop_ip_field.hide()
            self.next_hop_ip_field.is_optional = True
            if hasattr(self.next_hop_ip_field, 'error_label'):
                self.next_hop_ip_field.error_label.setText("")

            self.next_hop_interface_field.show()
            self.next_hop_interface_field.is_optional = False

    def validate_all(self):
        """
        Validates individual fields and enforces cross-field IPv4/IPv6 consistency using native field error handling.
        """
        is_valid = True

        if not self.fields["network"].validate():
            is_valid = False

        if not self.fields["mask"].validate():
            is_valid = False

        if not self.next_hop_type_field.validate():
            is_valid = False

        hop_type = self.next_hop_type_field.get_value()
        if hop_type == "IP Address":
            if not self.next_hop_ip_field.validate():
                is_valid = False
        elif hop_type == "Interface":
            if not self.next_hop_interface_field.validate():
                is_valid = False

        if not is_valid:
            return False

        network_version = self.fields["network"].get_ip_version()
        mask_val = self.fields["mask"].get_value()

        if network_version == "ipv4":
            if not InputValidator.is_valid_mask(mask_val):
                self.fields["mask"].highlight_error("Invalid mask or prefix")
                is_valid = False
            if hop_type == "IP Address" and self.next_hop_ip_field.get_ip_version() != "ipv4":
                self.next_hop_ip_field.highlight_error("Invalid IP address")
                is_valid = False

        elif network_version == "ipv6":
            if not InputValidator.is_valid_ipv6_prefix(mask_val):
                self.fields["mask"].highlight_error("Invalid mask or prefix")
                is_valid = False
            if hop_type == "IP Address" and self.next_hop_ip_field.get_ip_version() != "ipv6":
                self.next_hop_ip_field.highlight_error("Invalid IP address")
                is_valid = False

        return is_valid

    def update_interfaces(self, interfaces: list[str]):
        """
        Populates the interface dropdown with retrieved device data.
        """
        self.next_hop_interface_field.input_widget.clear()
        self.next_hop_interface_field.input_widget.addItems(interfaces)

    def get_data(self) -> dict:
        """
        Retrieves routing data alongside the resolved IP version.
        """
        hop_type = self.next_hop_type_field.get_value()
        next_hop_val = self.next_hop_ip_field.get_value() if hop_type == "IP Address" else self.next_hop_interface_field.get_value()

        return {
            "type": "static_routing",
            "version": self.fields["network"].get_ip_version(),
            "network": self.fields["network"].get_value(),
            "mask": self.fields["mask"].get_value(),
            "next_hop": next_hop_val,
            "_save_configuration": self.save_configuration_cb.isChecked()
        }