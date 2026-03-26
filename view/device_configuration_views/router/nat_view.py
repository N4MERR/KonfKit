from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal
from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.input_fields.dropdown_field import DropdownField
from view.device_configuration_views.input_fields.ip_address_field import IPAddressField
from view.device_configuration_views.input_fields.string_input_field import StringInputField
from view.device_configuration_views.input_fields.subnet_mask_field import SubnetMaskField
from view.device_configuration_views.input_fields.toggle_field import ToggleField


class NATInterfaceRoleView(BaseConfigView):
    """
    View handling NAT Interface Role Assignment.
    """
    load_interfaces_signal = Signal()

    def __init__(self):
        """
        Initializes fields for assigning NAT roles to interfaces.
        """
        super().__init__()

        self.load_interfaces_btn = QPushButton("Load Interfaces")
        self.load_interfaces_btn.setStyleSheet(
            "QPushButton { background-color: #cccccc; color: black; border: 1px solid #8a8886; border-radius: 4px; padding: 6px; font-weight: bold; }"
            "QPushButton:hover { background-color: #b3b3b3; }"
        )
        self.load_interfaces_btn.clicked.connect(self.load_interfaces_signal.emit)
        self.button_layout.insertWidget(0, self.load_interfaces_btn)

        self.interface_field = DropdownField("Select Interface:", [], is_optional=False)
        self.add_field("interface", self.interface_field)

        self.role_field = DropdownField("Inside/Outside:", ["inside", "outside"], is_optional=False)
        self.add_field("role", self.role_field)

    def update_interfaces(self, interfaces: list[str]):
        """
        Updates the interface selection dropdown.
        """
        self.interface_field.input_widget.clear()
        self.interface_field.input_widget.addItems(interfaces)

    def get_data(self) -> dict:
        """
        Retrieves data for interface role configuration.
        """
        return {
            "type": "interface_role",
            "interface": self.interface_field.get_value(),
            "role": self.role_field.get_value(),
            "_save_configuration": self.save_configuration_cb.isChecked()
        }


class NATPoolCreationView(BaseConfigView):
    """
    View handling new NAT Pool Creation.
    """

    def __init__(self):
        """
        Initializes the fields required to define a new IP NAT pool.
        """
        super().__init__()

        self.pool_name = StringInputField("New Pool Name:", max_length=64, allowed_chars="a-zA-Z0-9_-", start_with="a-zA-Z", is_optional=False)
        self.add_field("pool_name", self.pool_name)

        self.start_ip = IPAddressField("Start IP:", is_optional=False)
        self.add_field("start_ip", self.start_ip)

        self.end_ip = IPAddressField("End IP:", is_optional=False)
        self.add_field("end_ip", self.end_ip)

        self.netmask = SubnetMaskField("Netmask:", is_optional=False)
        self.add_field("netmask", self.netmask)

    def get_data(self) -> dict:
        """
        Retrieves data for establishing a new NAT pool.
        """
        return {
            "type": "pool_creation",
            "pool_name": self.pool_name.get_value(),
            "start_ip": self.start_ip.get_value(),
            "end_ip": self.end_ip.get_value(),
            "netmask": self.netmask.get_value(),
            "_save_configuration": self.save_configuration_cb.isChecked()
        }


class NATTranslationRuleView(BaseConfigView):
    """
    View handling NAT Translation Rules.
    """
    load_interfaces_signal = Signal()
    load_acls_signal = Signal()
    load_pools_signal = Signal()

    def __init__(self):
        """
        Initializes dynamic fields and triggers for generating translation rules.
        """
        super().__init__()

        self.load_interfaces_btn = QPushButton("Load Interfaces")
        self.load_interfaces_btn.setStyleSheet(
            "QPushButton { background-color: #cccccc; color: black; border: 1px solid #8a8886; border-radius: 4px; padding: 6px; font-weight: bold; }"
            "QPushButton:hover { background-color: #b3b3b3; }"
        )
        self.load_interfaces_btn.clicked.connect(self.load_interfaces_signal.emit)
        self.button_layout.insertWidget(0, self.load_interfaces_btn)

        self.load_acls_btn = QPushButton("Load ACLs")
        self.load_acls_btn.setStyleSheet(
            "QPushButton { background-color: #cccccc; color: black; border: 1px solid #8a8886; border-radius: 4px; padding: 6px; font-weight: bold; }"
            "QPushButton:hover { background-color: #b3b3b3; }"
        )
        self.load_acls_btn.clicked.connect(self.load_acls_signal.emit)
        self.button_layout.insertWidget(1, self.load_acls_btn)

        self.load_pools_btn = QPushButton("Load Pools")
        self.load_pools_btn.setStyleSheet(
            "QPushButton { background-color: #cccccc; color: black; border: 1px solid #8a8886; border-radius: 4px; padding: 6px; font-weight: bold; }"
            "QPushButton:hover { background-color: #b3b3b3; }"
        )
        self.load_pools_btn.clicked.connect(self.load_pools_signal.emit)
        self.button_layout.insertWidget(2, self.load_pools_btn)

        self.source_type_field = DropdownField("Source:", ["static", "access control list"], is_optional=False)
        self.add_field("source_type", self.source_type_field)
        self.source_type_field.input_widget.currentTextChanged.connect(self._toggle_fields)

        self.inside_ip = IPAddressField("Inside Local IP:", is_optional=False)
        self.add_field("inside_ip", self.inside_ip)

        self.outside_ip = IPAddressField("Outside Global IP:", is_optional=False)
        self.add_field("outside_ip", self.outside_ip)

        self.acl_field = DropdownField("ACL:", [], is_optional=False)
        self.add_field("acl", self.acl_field)

        self.mapping_type_field = DropdownField("Map to:", ["interface", "pool"], is_optional=False)
        self.add_field("mapping_type", self.mapping_type_field)
        self.mapping_type_field.input_widget.currentTextChanged.connect(self._toggle_fields)

        self.target_interface_field = DropdownField("Interface:", [], is_optional=False)
        self.add_field("target_interface", self.target_interface_field)

        self.pool_field = DropdownField("Pool:", [], is_optional=False)
        self.add_field("pool", self.pool_field)

        self.overload_field = ToggleField("Overload:", is_optional=False)
        self.add_field("overload", self.overload_field)

        self._toggle_fields()

    def _toggle_fields(self):
        """
        Manages the visibility of conditional fields based on the selected configuration options.
        """
        source_type = self.source_type_field.get_value()
        is_static = source_type == "static"
        is_list = source_type == "access control list"

        self.inside_ip.setVisible(is_static)
        self.outside_ip.setVisible(is_static)

        self.acl_field.setVisible(is_list)
        self.mapping_type_field.setVisible(is_list)
        self.overload_field.setVisible(is_list)

        mapping_type = self.mapping_type_field.get_value()
        self.target_interface_field.setVisible(is_list and mapping_type == "interface")
        self.pool_field.setVisible(is_list and mapping_type == "pool")

    def validate_all(self) -> bool:
        """
        Performs validation only on fields that are currently visible to the user.
        """
        is_valid = True
        for field in self.fields.values():
            if field.isVisible() and hasattr(field, 'validate'):
                if not field.validate():
                    is_valid = False
        return is_valid

    def update_interfaces(self, interfaces: list[str]):
        """
        Updates target interface selection dropdowns with available data from the device.
        """
        self.target_interface_field.input_widget.clear()
        self.target_interface_field.input_widget.addItems(interfaces)

    def update_acls(self, acls: list[str]):
        """
        Updates the access list dropdown with available data from the device.
        """
        self.acl_field.input_widget.clear()
        self.acl_field.input_widget.addItems(acls)

    def update_pools(self, pools: list[str]):
        """
        Updates the NAT pool dropdown with available data from the device.
        """
        self.pool_field.input_widget.clear()
        self.pool_field.input_widget.addItems(pools)

    def get_data(self) -> dict:
        """
        Retrieves configuration data only from the fields currently visible in the UI.
        """
        data = {
            "type": "translation_rule",
            "source_type": self.source_type_field.get_value(),
            "_save_configuration": self.save_configuration_cb.isChecked()
        }

        if self.inside_ip.isVisible():
            data["inside_ip"] = self.inside_ip.get_value()
        if self.outside_ip.isVisible():
            data["outside_ip"] = self.outside_ip.get_value()
        if self.acl_field.isVisible():
            data["acl"] = self.acl_field.get_value()
        if self.mapping_type_field.isVisible():
            data["mapping_type"] = self.mapping_type_field.get_value()
        if self.target_interface_field.isVisible():
            data["target_interface"] = self.target_interface_field.get_value()
        if self.pool_field.isVisible():
            data["pool"] = self.pool_field.get_value()
        if self.overload_field.isVisible():
            data["overload"] = self.overload_field.get_value()

        return data


class NATView:
    """
    Container class aggregating NAT configuration subsections.
    """

    def __init__(self):
        """
        Initializes individual NAT configuration categories.
        """
        self.interface_role = NATInterfaceRoleView()
        self.pool_creation = NATPoolCreationView()
        self.translation_rule = NATTranslationRuleView()