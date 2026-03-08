from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.input_fields.base_input_field import BaseInputField
from view.device_configuration_views.input_fields.ip_address_field import IPAddressField
from view.device_configuration_views.input_fields.wildcard_mask_field import WildcardMaskField
from view.device_configuration_views.input_fields.ranged_number_field import RangedNumberField
from view.device_configuration_views.input_fields.interface_field import InterfaceField

class OSPFBasicView(BaseConfigView):
    """
    View handling OSPF network advertisements.
    """

    def __init__(self):
        """
        Initializes the OSPF network advertisement view with strict parameters.
        """
        super().__init__()

        self.add_field("process_id", RangedNumberField("Process ID (1-65535):", 1, 65535, is_optional=False))
        self.add_field("network", IPAddressField("Network:", is_optional=False))
        self.add_field("wildcard_mask", WildcardMaskField("Wildcard Mask:", is_optional=False))
        self.add_field("area", RangedNumberField("Area:", 0, 2147483647, is_optional=False))

    def get_data(self) -> dict:
        """
        Retrieves data for OSPF network advertisements.
        """
        return {
            "type": "basic",
            "process_id": self.fields["process_id"].get_value(),
            "network": self.fields["network"].get_value(),
            "wildcard_mask": self.fields["wildcard_mask"].get_value(),
            "area": self.fields["area"].get_value(),
            "_write_memory": self.write_memory_cb.isChecked()
        }

class OSPFRouterIdView(BaseConfigView):
    """
    View handling OSPF Router ID configuration.
    """

    def __init__(self):
        """
        Initializes the OSPF Router ID view with strict parameters.
        """
        super().__init__()

        self.add_field("process_id", RangedNumberField("Process ID (1-65535):", 1, 65535, is_optional=False))
        self.add_field("router_id", IPAddressField("Router ID:", is_optional=False))

    def get_data(self) -> dict:
        """
        Retrieves data for OSPF Router ID configuration.
        """
        return {
            "type": "router_id",
            "process_id": self.fields["process_id"].get_value(),
            "router_id": self.fields["router_id"].get_value(),
            "_write_memory": self.write_memory_cb.isChecked()
        }

class OSPFPassiveInterfaceView(BaseConfigView):
    """
    View handling OSPF passive interfaces.
    """

    def __init__(self):
        """
        Initializes the OSPF Passive Interface view with strict parameters.
        """
        super().__init__()

        self.add_field("process_id", RangedNumberField("Process ID (1-65535):", 1, 65535, is_optional=False))
        self.add_field("interface_name", InterfaceField("Interface Name:", is_optional=False))

    def get_data(self) -> dict:
        """
        Retrieves data for OSPF passive interface configuration.
        """
        return {
            "type": "passive_interface",
            "process_id": self.fields["process_id"].get_value(),
            "interface_name": self.fields["interface_name"].get_value(),
            "_write_memory": self.write_memory_cb.isChecked()
        }

class OSPFView:
    """
    Container class aggregating OSPF configuration subsections.
    """

    def __init__(self):
        """
        Initializes OSPF subsections.
        """
        self.basic_config = OSPFBasicView()
        self.router_id = OSPFRouterIdView()
        self.passive_interfaces = OSPFPassiveInterfaceView()
