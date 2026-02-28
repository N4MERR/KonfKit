"""
Section for creating and naming VLANs with proper data retrieval.
"""
from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.config_fields import (
    BaseConfigField, NumberField
)

class VLANView(BaseConfigView):
    """
    Section for creating and naming VLANs.
    """

    def __init__(self):
        """
        Initializes VLAN configuration fields.
        """
        super().__init__()
        vlan_id = self.add_field("vlan_id", NumberField("VLAN ID:"))
        vlan_id.set_error_message("Enter a valid VLAN ID (1-4094).")

        vlan_name = self.add_field("vlan_name", BaseConfigField("VLAN Name:", is_optional=True))
        vlan_name.set_error_message("Name cannot be empty if enabled.")

    def get_data(self) -> dict:
        """
        Retrieves data for VLAN configuration using the radio indicator.
        """
        return {
            "type": "vlan",
            "vlan_id": self.fields["vlan_id"].get_value(),
            "vlan_name": self.fields["vlan_name"].get_value(),
            "name_enabled": self.fields["vlan_name"].radio.isChecked()
        }