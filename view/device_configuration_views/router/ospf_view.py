"""
OSPF configuration views with corrected data retrieval for validation and a unified container.
"""
from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.config_fields import (
    BaseConfigField, IPAddressField, NumberField
)


class OSPFBasicView(BaseConfigView):
    """
    View handling OSPF network advertisements.
    """

    def __init__(self):
        """
        Initializes the OSPF network advertisement view.
        """
        super().__init__()

        process_id = self.add_field("process_id", NumberField("Process ID:"))
        process_id.set_error_message("Process ID must be a valid number.")

        network = self.add_field("network", IPAddressField("Network:"))
        network.set_error_message("Invalid IPv4 network address.")

        wildcard = self.add_field("wildcard_mask", IPAddressField("Wildcard Mask:"))
        wildcard.set_error_message("Invalid wildcard mask format.")

        area = self.add_field("area", NumberField("Area:"))
        area.set_error_message("Area must be a valid number.")

    def get_data(self) -> dict:
        """
        Retrieves data for OSPF network advertisements.
        """
        return {
            "type": "basic",
            "process_id": self.fields["process_id"].get_value(),
            "network": self.fields["network"].get_value(),
            "wildcard_mask": self.fields["wildcard_mask"].get_value(),
            "area": self.fields["area"].get_value()
        }


class OSPFRouterIdView(BaseConfigView):
    """
    View handling OSPF Router ID configuration.
    """

    def __init__(self):
        """
        Initializes the OSPF Router ID view.
        """
        super().__init__()

        process_id = self.add_field("process_id", NumberField("Process ID:"))
        process_id.set_error_message("Process ID must be a valid number.")

        router_id = self.add_field("router_id", IPAddressField("Router ID:"))
        router_id.set_error_message("Router ID must be a valid IPv4 address.")

    def get_data(self) -> dict:
        """
        Retrieves data for OSPF Router ID configuration.
        """
        return {
            "type": "router_id",
            "process_id": self.fields["process_id"].get_value(),
            "router_id": self.fields["router_id"].get_value()
        }


class OSPFPassiveInterfaceView(BaseConfigView):
    """
    View handling OSPF passive interfaces.
    """

    def __init__(self):
        """
        Initializes the OSPF Passive Interface view.
        """
        super().__init__()

        process_id = self.add_field("process_id", NumberField("Process ID:"))
        process_id.set_error_message("Process ID must be a valid number.")

        interface = self.add_field("interface_name", BaseConfigField("Interface Name:"))
        interface.set_error_message("Interface name cannot be empty.")

    def get_data(self) -> dict:
        """
        Retrieves data for OSPF passive interface configuration.
        """
        return {
            "type": "passive_interface",
            "process_id": self.fields["process_id"].get_value(),
            "interface_name": self.fields["interface_name"].get_value()
        }


class OSPFDefaultRouteView(BaseConfigView):
    """
    View handling OSPF default route advertisement.
    """

    def __init__(self):
        """
        Initializes the OSPF Default Route view.
        """
        super().__init__()

        process_id = self.add_field("process_id", NumberField("Process ID:"))
        process_id.set_error_message("Process ID must be a valid number.")

        self.add_field("always", BaseConfigField("Always originate:", is_optional=True))

    def get_data(self) -> dict:
        """
        Retrieves data for OSPF default route advertisement.
        """
        return {
            "type": "default_route",
            "process_id": self.fields["process_id"].get_value(),
            "always": self.fields["always"].checkbox.isChecked()
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
        self.default_route = OSPFDefaultRouteView()