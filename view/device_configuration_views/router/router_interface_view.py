from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal
from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.input_fields.dropdown_field import DropdownField
from view.device_configuration_views.input_fields.ip_address_field import IPAddressField
from view.device_configuration_views.input_fields.ipv6_address_field import IPv6AddressField
from view.device_configuration_views.input_fields.ipv6_prefix_length_field import IPv6PrefixField
from view.device_configuration_views.input_fields.subnet_mask_field import SubnetMaskField
from view.device_configuration_views.input_fields.number_field import NumberField
from view.device_configuration_views.input_fields.radio_indicator_field import RadioIndicatorField


class BaseRouterInterfaceView(BaseConfigView):
    """
    Base view for loading interfaces and providing the selection dropdown.
    """
    refresh_interfaces_signal = Signal()

    def __init__(self):
        """
        Initializes the interface layout with a fetch button placed in the bottom left corner and an interface selection.
        """
        super().__init__()

        self.refresh_btn = QPushButton("Load Interfaces")
        self.refresh_btn.setStyleSheet(
            "QPushButton { background-color: #cccccc; color: black; border: 1px solid #8a8886; border-radius: 4px; padding: 6px; font-weight: bold; }"
            "QPushButton:hover { background-color: #b3b3b3; }"
            "QPushButton:disabled { background-color: #e6e6e6; color: #a0a0a0; border: 1px solid #c0c0c0; }"
        )
        self.refresh_btn.clicked.connect(self.refresh_interfaces_signal.emit)
        self.button_layout.insertWidget(0, self.refresh_btn)

        self.interface_dropdown = DropdownField("Select Interface:", [], is_optional=False)
        self.add_field("interface", self.interface_dropdown)

    def update_interfaces(self, interfaces: list[str]):
        """
        Populates the interface dropdown with retrieved device data using the correct base widget attribute.
        """
        self.interface_dropdown.input_widget.clear()
        self.interface_dropdown.input_widget.addItems(interfaces)

    def validate_all(self) -> bool:
        """
        Overrides base validation to ensure at least one IP protocol is enabled and conditional mask validation.
        """
        ipv4_enabled = self.fields["ip_address"].radio.isChecked()
        ipv6_enabled = self.fields["ipv6_address"].radio.isChecked()

        self.fields["subnet_mask"].is_optional = not ipv4_enabled
        self.fields["ipv6_prefix"].is_optional = not ipv6_enabled

        base_valid = super().validate_all()

        if not ipv4_enabled and not ipv6_enabled:
            self.fields["ip_address"].set_error_message("At least one address is required")
            self.fields["ipv6_address"].set_error_message("At least one address is required")
            self.fields["ip_address"].highlight_error("At least one address is required")
            self.fields["ipv6_address"].highlight_error("At least one address is required")
            return False

        self.fields["ip_address"].set_error_message("Invalid IP address")
        self.fields["ipv6_address"].set_error_message("Invalid IPv6 address")

        return base_valid


class RouterPhysicalInterfaceView(BaseRouterInterfaceView):
    """
    View dedicated to configuring standard physical interfaces on the router.
    """

    def __init__(self):
        """
        Initializes fields relevant for physical interfaces including dual-stack options.
        """
        super().__init__()

        ipv4_field = IPAddressField("IPv4 Address:", is_optional=True)
        self.add_field("ip_address", ipv4_field)
        self.add_field("subnet_mask", SubnetMaskField("Subnet Mask:", is_optional=False, linked_ip_field=ipv4_field))

        ipv6_field = IPv6AddressField("IPv6 Address:", is_optional=True)
        self.add_field("ipv6_address", ipv6_field)
        self.add_field("ipv6_prefix", IPv6PrefixField("IPv6 Prefix:", is_optional=False, linked_ip_field=ipv6_field))

        self.enable_interface = RadioIndicatorField("Enable Interface (no shutdown)")
        self.form_layout.insertWidget(self.form_layout.count() - 1, self.enable_interface)

    def get_data(self) -> dict:
        """
        Collects physical interface configuration data for both IP versions and optional states.
        """
        return {
            "type": "physical",
            "interface": self.fields["interface"].get_value(),
            "ip_address": self.fields["ip_address"].get_value(),
            "ip_enabled": self.fields["ip_address"].radio.isChecked(),
            "subnet_mask": self.fields["subnet_mask"].get_value(),
            "ipv6_address": self.fields["ipv6_address"].get_value(),
            "ipv6_enabled": self.fields["ipv6_address"].radio.isChecked(),
            "ipv6_prefix": self.fields["ipv6_prefix"].get_value(),
            "enable_interface": self.enable_interface.isChecked(),
            "_save_configuration": self.save_configuration_cb.isChecked()
        }


class RouterSubinterfaceView(BaseRouterInterfaceView):
    """
    View dedicated to configuring 802.1Q subinterfaces on the router.
    """

    def __init__(self):
        """
        Initializes fields relevant for dot1Q subinterfaces including dual-stack options.
        """
        super().__init__()

        self.add_field("subinterface_id", NumberField("Subinterface ID:", is_optional=False))
        self.add_field("vlan_id", NumberField("VLAN ID (dot1Q):", is_optional=False))

        ipv4_field = IPAddressField("IPv4 Address:", is_optional=True)
        self.add_field("ip_address", ipv4_field)
        self.add_field("subnet_mask", SubnetMaskField("Subnet Mask:", is_optional=False, linked_ip_field=ipv4_field))

        ipv6_field = IPv6AddressField("IPv6 Address:", is_optional=True)
        self.add_field("ipv6_address", ipv6_field)
        self.add_field("ipv6_prefix", IPv6PrefixField("IPv6 Prefix:", is_optional=False, linked_ip_field=ipv6_field))

    def get_data(self) -> dict:
        """
        Collects subinterface configuration data for both IP versions and optional states.
        """
        return {
            "type": "subinterface",
            "interface": self.fields["interface"].get_value(),
            "subinterface_id": self.fields["subinterface_id"].get_value(),
            "vlan_id": self.fields["vlan_id"].get_value(),
            "ip_address": self.fields["ip_address"].get_value(),
            "ip_enabled": self.fields["ip_address"].radio.isChecked(),
            "subnet_mask": self.fields["subnet_mask"].get_value(),
            "ipv6_address": self.fields["ipv6_address"].get_value(),
            "ipv6_enabled": self.fields["ipv6_address"].radio.isChecked(),
            "ipv6_prefix": self.fields["ipv6_prefix"].get_value(),
            "_save_configuration": self.save_configuration_cb.isChecked()
        }


class RouterInterfaceView:
    """
    Container aggregating independent router interface configuration views.
    """

    def __init__(self):
        """
        Instantiates specific physical and subinterface views.
        """
        self.physical = RouterPhysicalInterfaceView()
        self.subinterface = RouterSubinterfaceView()