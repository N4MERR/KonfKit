from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal
from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.input_fields.ip_address_field import IPAddressField
from view.device_configuration_views.input_fields.subnet_mask_field import SubnetMaskField
from view.device_configuration_views.input_fields.dropdown_field import DropdownField


class StaticRoutingView(BaseConfigView):
    """
    View handling router static routing configuration with dynamic next hop selection.
    """
    load_interfaces_signal = Signal()

    def __init__(self):
        """
        Initializes the static routing view with dynamic fields for next hop type and a load interfaces button.
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

        self.add_field("network", IPAddressField("Network IP:", is_optional=False))
        self.add_field("mask", SubnetMaskField("Subnet Mask:", is_optional=False))

        self.next_hop_type_field = DropdownField("Next Hop Type:", ["IP Address", "Interface"], is_optional=False)
        self.add_field("next_hop_type", self.next_hop_type_field)

        self.next_hop_ip_field = IPAddressField("Next Hop IP:", is_optional=False)
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
        Overrides the base validation to ensure hidden fields do not block configuration submission.
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

        return is_valid

    def update_interfaces(self, interfaces: list[str]):
        """
        Populates the interface dropdown with retrieved device data.
        """
        self.next_hop_interface_field.input_widget.clear()
        self.next_hop_interface_field.input_widget.addItems(interfaces)

    def get_data(self) -> dict:
        """
        Retrieves data for static routing configuration dynamically based on the selected next hop type.
        """
        hop_type = self.next_hop_type_field.get_value()
        next_hop_val = self.next_hop_ip_field.get_value() if hop_type == "IP Address" else self.next_hop_interface_field.get_value()

        return {
            "type": "static_routing",
            "network": self.fields["network"].get_value(),
            "mask": self.fields["mask"].get_value(),
            "next_hop": next_hop_val,
            "_save_configuration": self.save_configuration_cb.isChecked()
        }