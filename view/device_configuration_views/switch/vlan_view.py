from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.input_fields.dropdown_field import DropdownField
from view.device_configuration_views.input_fields.multi_select_list_field import MultiSelectListField
from view.device_configuration_views.input_fields.ranged_number_field import RangedNumberField
from view.device_configuration_views.input_fields.base_input_field import BaseInputField
from view.device_configuration_views.input_fields.ip_address_field import IPAddressField
from view.device_configuration_views.input_fields.subnet_mask_field import SubnetMaskField
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal


class CreateVlanView(BaseConfigView):
    """
    View for creating a VLAN in the VLAN database and optionally configuring its Switch Virtual Interface.
    """

    def __init__(self):
        """
        Initializes the fields for VLAN ID, Name, IP Address, and Subnet Mask, enforcing their dynamic states.
        """
        super().__init__()

        self.vlan_id_field = RangedNumberField("VLAN ID (1-4094):", 1, 4094, is_optional=False)
        self.add_field("vlan_id", self.vlan_id_field)

        self.vlan_name_field = BaseInputField("VLAN Name:", is_optional=True)
        self.add_field("vlan_name", self.vlan_name_field)

        self.vlan_ip_field = IPAddressField("VLAN IP Address:", is_optional=True)
        self.add_field("vlan_ip", self.vlan_ip_field)

        self.vlan_mask_field = SubnetMaskField("Subnet Mask:", is_optional=True)
        self.add_field("vlan_mask", self.vlan_mask_field)

        if hasattr(self.vlan_mask_field, 'radio'):
            self.vlan_mask_field.radio.setEnabled(False)

        if hasattr(self.vlan_ip_field, 'radio'):
            self.vlan_ip_field.radio.toggled.connect(self._sync_subnet_mask_state)
            self._sync_subnet_mask_state(self.vlan_ip_field.radio.isChecked())

    def _sync_subnet_mask_state(self, checked: bool):
        """
        Synchronizes the state of the subnet mask field with the IP address field.
        """
        if hasattr(self.vlan_mask_field, 'input_widget'):
            self.vlan_mask_field.input_widget.setEnabled(checked)

        if hasattr(self.vlan_mask_field, 'radio'):
            self.vlan_mask_field.radio.setChecked(checked)

        if not checked and hasattr(self.vlan_mask_field, 'input_widget'):
            self.vlan_mask_field.input_widget.clear()

    def get_data(self) -> dict:
        """
        Retrieves the VLAN creation configuration data from the input fields.
        """
        return {
            "type": "create_vlan",
            "vlan_id": self.vlan_id_field.get_value(),
            "vlan_name": self.vlan_name_field.get_value() if hasattr(self.vlan_name_field,
                                                                     'radio') and self.vlan_name_field.radio.isChecked() else None,
            "vlan_ip": self.vlan_ip_field.get_value() if hasattr(self.vlan_ip_field,
                                                                 'radio') and self.vlan_ip_field.radio.isChecked() else None,
            "vlan_mask": self.vlan_mask_field.get_value() if hasattr(self.vlan_mask_field,
                                                                     'radio') and self.vlan_mask_field.radio.isChecked() else None,
            "_save_configuration": self.save_configuration_cb.isChecked()
        }


class InterfaceVlanView(BaseConfigView):
    """
    View handling VLAN configuration for interfaces, supporting dynamic switching between access and trunk modes.
    """
    load_interfaces_signal = Signal()
    load_vlans_signal = Signal()

    def __init__(self):
        """
        Initializes the interface selection, mode selection, conditional access/trunk VLAN fields, and optional native VLAN.
        """
        super().__init__()

        self._current_locked_native_vlan = None

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

        self.interface_field = DropdownField("Select Interface:", [], is_optional=False)
        self.add_field("interface", self.interface_field)

        self.mode_field = DropdownField("Mode:", ["access", "trunk"], is_optional=False)
        self.add_field("mode", self.mode_field)
        self.mode_field.input_widget.currentTextChanged.connect(self.toggle_vlan_fields)

        self.access_vlan_field = DropdownField("Select Access VLAN:", [], is_optional=False)
        self.add_field("access_vlan", self.access_vlan_field)

        self.trunk_vlans_field = MultiSelectListField("Allowed Trunk VLANs:", is_optional=False, min_selections=1)
        self.add_field("trunk_vlans", self.trunk_vlans_field)

        self.native_vlan_field = DropdownField("Native VLAN:", [], is_optional=True)
        self.add_field("native_vlan", self.native_vlan_field)

        self.native_vlan_field.input_widget.currentTextChanged.connect(self._update_native_vlan_lock)
        if hasattr(self.native_vlan_field, 'radio'):
            self.native_vlan_field.radio.stateChanged.connect(self._update_native_vlan_lock)

        self.toggle_vlan_fields(self.mode_field.get_value())

    def _update_native_vlan_lock(self, *args):
        """
        Synchronizes the selected Native VLAN with the Allowed Trunk VLANs list.
        """
        if self.mode_field.get_value() != "trunk":
            return

        is_native_enabled = False
        if hasattr(self.native_vlan_field, 'radio'):
            is_native_enabled = self.native_vlan_field.radio.isChecked()
        else:
            is_native_enabled = True

        selected_vlan = self.native_vlan_field.get_value()

        if self._current_locked_native_vlan and (
                not is_native_enabled or self._current_locked_native_vlan != selected_vlan):
            self.trunk_vlans_field.unlock_and_uncheck_item(self._current_locked_native_vlan)
            self._current_locked_native_vlan = None

        if is_native_enabled and selected_vlan:
            self.trunk_vlans_field.force_select_and_lock(selected_vlan)
            self._current_locked_native_vlan = selected_vlan

    def toggle_vlan_fields(self, mode: str):
        """
        Toggles the visibility of VLAN selection fields depending on the active interface mode
        """
        if mode == "access":
            self.access_vlan_field.show()
            self.access_vlan_field.is_optional = False

            self.trunk_vlans_field.hide()
            self.trunk_vlans_field.is_optional = True

            if hasattr(self.trunk_vlans_field, 'error_label'):
                self.trunk_vlans_field.error_label.setText("")

            self.native_vlan_field.hide()
        else:
            self.access_vlan_field.hide()
            self.access_vlan_field.is_optional = True

            if hasattr(self.access_vlan_field, 'error_label'):
                self.access_vlan_field.error_label.setText("")

            self.trunk_vlans_field.show()
            self.trunk_vlans_field.is_optional = False

            self.native_vlan_field.show()

        self._update_native_vlan_lock()

    def validate_all(self):
        """
        Overrides the base validation to ensure hidden fields do not block configuration submission.
        """
        is_valid = True

        if not self.interface_field.validate():
            is_valid = False

        if not self.mode_field.validate():
            is_valid = False

        mode = self.mode_field.get_value()
        if mode == "access":
            if not self.access_vlan_field.validate():
                is_valid = False
        elif mode == "trunk":
            if not self.trunk_vlans_field.validate():
                is_valid = False
            if not self.native_vlan_field.validate():
                is_valid = False

        return is_valid

    def update_interfaces(self, interfaces: list[str]):
        """
        Populates the interface dropdown with retrieved device data.
        """
        self.interface_field.input_widget.clear()
        self.interface_field.input_widget.addItems(interfaces)

    def update_vlans(self, vlans: list[str]):
        """
        Populates the access dropdown, trunk multi-select list, and native VLAN dropdown with retrieved VLAN data.
        """
        self.access_vlan_field.input_widget.clear()
        self.access_vlan_field.input_widget.addItems(vlans)

        self._current_locked_native_vlan = None
        self.trunk_vlans_field.populate_items(vlans)

        self.native_vlan_field.input_widget.blockSignals(True)
        self.native_vlan_field.input_widget.clear()
        self.native_vlan_field.input_widget.addItems(vlans)
        self.native_vlan_field.input_widget.blockSignals(False)

        self._update_native_vlan_lock()

    def get_data(self) -> dict:
        """
        Retrieves selected interface, mode, and the corresponding VLAN parameters based on mode.
        """
        mode = self.mode_field.get_value()
        native_val = None
        if mode == "trunk" and hasattr(self.native_vlan_field, 'radio') and self.native_vlan_field.radio.isChecked():
            native_val = self.native_vlan_field.get_value()

        return {
            "type": "vlan",
            "interface": self.interface_field.get_value(),
            "mode": mode,
            "access_vlan": self.access_vlan_field.get_value() if mode == "access" else None,
            "trunk_vlans": self.trunk_vlans_field.get_value() if mode == "trunk" else [],
            "native_vlan": native_val,
            "_save_configuration": self.save_configuration_cb.isChecked()
        }


class VlanView:
    """
    Container class aggregating VLAN configuration subsections.
    """

    def __init__(self):
        """
        Initializes VLAN subsections.
        """
        self.create_vlan = CreateVlanView()
        self.interface_vlan = InterfaceVlanView()