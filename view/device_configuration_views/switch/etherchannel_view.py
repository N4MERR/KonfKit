from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.input_fields.dropdown_field import DropdownField
from view.device_configuration_views.input_fields.ranged_number_field import RangedNumberField
from view.device_configuration_views.input_fields.multi_select_list_field import MultiSelectListField
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal


class EtherChannelView(BaseConfigView):
    """
    View handling EtherChannel configuration, including flexible multi-interface selection and dynamic VLAN trunking parameters.
    """
    load_interfaces_signal = Signal()
    load_vlans_signal = Signal()

    def __init__(self):
        """
        Initializes the interface list with flexible boundaries (1-8), channel mode fields, and the automatic trunking VLAN list.
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

        self.load_vlans_btn = QPushButton("Load VLANs")
        self.load_vlans_btn.setStyleSheet(
            "QPushButton { background-color: #cccccc; color: black; border: 1px solid #8a8886; border-radius: 4px; padding: 6px; font-weight: bold; }"
            "QPushButton:hover { background-color: #b3b3b3; }"
            "QPushButton:disabled { background-color: #e6e6e6; color: #a0a0a0; border: 1px solid #c0c0c0; }"
        )
        self.load_vlans_btn.clicked.connect(self.load_vlans_signal.emit)
        self.button_layout.insertWidget(1, self.load_vlans_btn)

        self.interface_list = MultiSelectListField("Select EtherChannel Interfaces:", is_optional=False, min_selections=1, max_selections=8)
        self.add_field("etherchannel", self.interface_list)

        self.add_field("channel_group", RangedNumberField("Channel Group (1-6):", 1, 6, is_optional=False))
        self.add_field("channel_mode", DropdownField("Mode:", ["active", "passive", "desirable", "auto", "on"], is_optional=False))

        self.vlan_list = MultiSelectListField("Allowed VLANs (Automatically sets Trunk Mode):", is_optional=True)
        self.add_field("allowed_vlans", self.vlan_list)

    def update_interfaces(self, interfaces: list[str]):
        """
        Populates the multi-select interface list with retrieved device data.
        """
        self.interface_list.populate_items(interfaces)

    def update_vlans(self, vlans: list[str]):
        """
        Populates the multi-select VLAN list with retrieved device data.
        """
        self.vlan_list.populate_items(vlans)

    def get_data(self) -> dict:
        """
        Retrieves selected interfaces, group data, and optional allowed VLANs.
        """
        return {
            "type": "etherchannel",
            "etherchannel": self.fields["etherchannel"].get_value(),
            "channel_group": self.fields["channel_group"].get_value(),
            "channel_mode": self.fields["channel_mode"].get_value(),
            "allowed_vlans": self.fields["allowed_vlans"].get_value() if self.fields["allowed_vlans"].radio.isChecked() else [],
            "_save_configuration": self.save_configuration_cb.isChecked()
        }