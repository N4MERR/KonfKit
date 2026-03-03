from PySide6.QtWidgets import QCheckBox
from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.config_fields import (
    BaseConfigField, RangedNumberField
)


class VLANView(BaseConfigView):
    """
    Section for creating and naming VLANs.
    """

    def __init__(self):
        """
        Initializes VLAN configuration fields with strict validation and write memory options.
        """
        super().__init__()

        self.add_field("vlan_id", RangedNumberField("VLAN ID (1-4094):", 1, 4094, is_optional=False))
        self.add_field("vlan_name", BaseConfigField("VLAN Name:", is_optional=True))

        self.write_memory_cb = QCheckBox("Write Memory")
        self.button_layout.insertWidget(0, self.write_memory_cb)

    def get_data(self) -> dict:
        """
        Retrieves data for VLAN configuration including the write memory state.
        """
        return {
            "type": "vlan",
            "vlan_id": self.fields["vlan_id"].get_value(),
            "vlan_name": self.fields["vlan_name"].get_value(),
            "name_enabled": self.fields["vlan_name"].radio.isChecked(),
            "_write_memory": self.write_memory_cb.isChecked()
        }