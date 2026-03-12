from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.input_fields.base_input_field import BaseInputField
from view.device_configuration_views.input_fields.ip_address_field import IPAddressField
from view.device_configuration_views.input_fields.subnet_mask_field import SubnetMaskField


class DHCPPoolView(BaseConfigView):
    """
    View handling parameters for a DHCP pool including network and optional services.
    """

    def __init__(self):
        """
        Initializes the DHCP pool fields and sets up the standard action buttons.
        """
        super().__init__()

        self.add_field("pool_name", BaseInputField("Pool Name:", is_optional=False))
        self.add_field("network", IPAddressField("Network Address:", is_optional=False))
        self.add_field("mask", SubnetMaskField("Subnet Mask:", is_optional=False))
        self.add_field("gateway", IPAddressField("Default Gateway:", is_optional=True))
        self.add_field("dns", IPAddressField("DNS Server:", is_optional=True))
        self.add_field("domain_name", BaseInputField("Domain Name:", is_optional=True))

    def get_data(self) -> dict:
        """
        Retrieves formatted data for DHCP pool configuration.
        """
        return {
            "type": "dhcp_pool",
            "pool_name": self.fields["pool_name"].get_value(),
            "network": self.fields["network"].get_value(),
            "mask": self.fields["mask"].get_value(),
            "gateway": self.fields["gateway"].get_value() if self.fields["gateway"].radio.isChecked() else None,
            "dns": self.fields["dns"].get_value() if self.fields["dns"].radio.isChecked() else None,
            "domain_name": self.fields["domain_name"].get_value() if self.fields["domain_name"].radio.isChecked() else None,
            "_write_memory": self.write_memory_cb.isChecked()
        }


class DHCPExcludedView(BaseConfigView):
    """
    View handling the exclusion of IP addresses from DHCP pools.
    """

    def __init__(self):
        """
        Initializes fields for defining excluded addresses and sets up action buttons.
        """
        super().__init__()

        self.add_field("start_ip", IPAddressField("Start IP Address:", is_optional=False))
        self.add_field("end_ip", IPAddressField("End IP Address (Optional):", is_optional=True))

    def get_data(self) -> dict:
        """
        Retrieves formatted data for excluded DHCP addresses.
        """
        return {
            "type": "dhcp_excluded",
            "start_ip": self.fields["start_ip"].get_value(),
            "end_ip": self.fields["end_ip"].get_value() if self.fields["end_ip"].radio.isChecked() else None,
            "_write_memory": self.write_memory_cb.isChecked()
        }

class DHCPView:
    """
        Container class aggregating DHCP configuration subsections.
        """

    def __init__(self):
        """
        Initializes DHCP subsections.
        """
        self.pool_view = DHCPPoolView()
        self.excluded_view = DHCPExcludedView()