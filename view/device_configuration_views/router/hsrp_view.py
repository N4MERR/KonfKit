from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.input_fields.base_input_field import BaseInputField
from view.device_configuration_views.input_fields.ip_address_field import IPAddressField
from view.device_configuration_views.input_fields.subnet_mask_field import SubnetMaskField
from view.device_configuration_views.input_fields.dropdown_field import DropdownField
from view.device_configuration_views.input_fields.ranged_number_field import RangedNumberField
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal


class HSRPView(BaseConfigView):
    """
    View handling HSRP configuration for router interfaces.
    """
    load_interfaces_signal = Signal()

    def __init__(self):
        """
        Initializes the interface dropdown, IP configuration, and HSRP specific fields.
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

        self.interface_dropdown = DropdownField("Interface:", [], is_optional=False)
        self.add_field("interface", self.interface_dropdown)

        self.add_field("ip_address", IPAddressField("Interface IP Address:", is_optional=True))
        self.add_field("subnet_mask", SubnetMaskField("Interface Subnet Mask:", is_optional=True))

        self.add_field("standby_id", RangedNumberField("Standby ID (0-4095):", 0, 4095, is_optional=False))
        self.add_field("virtual_ip", IPAddressField("Virtual IP Address:", is_optional=False))
        self.add_field("priority", RangedNumberField("Priority (0-255):", 0, 255, is_optional=True))
        self.add_field("preempt", DropdownField("Preempt:", ["Disable", "Enable"], is_optional=True))

        self.fields["subnet_mask"].radio.setEnabled(False)
        self.fields["ip_address"].radio.toggled.connect(self._sync_subnet_mask_state)

        self._sync_subnet_mask_state(self.fields["ip_address"].radio.isChecked())

    def _sync_subnet_mask_state(self, checked: bool):
        """
        Synchronizes the state of the subnet mask field with the IP address field.
        """
        self.fields["subnet_mask"].input_widget.setEnabled(checked)
        self.fields["subnet_mask"].radio.setChecked(checked)
        if not checked:
            self.fields["subnet_mask"].input_widget.clear()

    def get_data(self) -> dict:
        """
        Retrieves HSRP configuration data.
        """
        ip_enabled = self.fields["ip_address"].radio.isChecked()

        return {
            "type": "hsrp_configuration",
            "interface": self.fields["interface"].get_value(),
            "ip_address": self.fields["ip_address"].get_value() if ip_enabled else "",
            "subnet_mask": self.fields["subnet_mask"].get_value() if ip_enabled else "",
            "standby_id": self.fields["standby_id"].get_value(),
            "virtual_ip": self.fields["virtual_ip"].get_value(),
            "priority": self.fields["priority"].get_value() if self.fields["priority"].radio.isChecked() else "",
            "preempt": self.fields["preempt"].get_value() if self.fields["preempt"].radio.isChecked() else "Disable",
            "_save_configuration": self.save_configuration_cb.isChecked()
        }

    def update_interfaces(self, interfaces: list[str]):
        """
        Populates the interface dropdown with retrieved device data.
        """
        self.interface_dropdown.input_widget.clear()
        self.interface_dropdown.input_widget.addItems(interfaces)