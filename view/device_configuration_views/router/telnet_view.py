from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.input_fields.base_input_field import BaseInputField
from view.device_configuration_views.input_fields.password_field import PasswordField
from view.device_configuration_views.input_fields.ranged_number_field import RangedNumberField
from view.device_configuration_views.input_fields.range_field import RangeField
from view.device_configuration_views.input_fields.dropdown_field import DropdownField
from view.device_configuration_views.input_fields.ip_address_field import IPAddressField
from view.device_configuration_views.input_fields.subnet_mask_field import SubnetMaskField
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal


class TelnetConnectionView(BaseConfigView):
    """
    View handling line transport, VTY lines, interface selection, and local login for Telnet on routers.
    """
    load_interfaces_signal = Signal()

    def __init__(self):
        """
        Initializes fields for interfaces, IP addressing, login methods, conditional credentials, and the save toggle.
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

        self.add_field("login_method", DropdownField("Login Method:", ["no login", "login local", "login"], is_optional=False))
        self.add_field("line_password", PasswordField("Line Password:", is_optional=True))

        self.add_field("login_username", BaseInputField("Login Username:", is_optional=True))
        self.add_field("login_password", PasswordField("Login Password:", is_optional=True))
        self.add_field("login_privilege", RangedNumberField("Privilege (0-15):", 0, 15, is_optional=True))

        self.vty_range = RangeField("VTY Line Range:", "vty_start", "vty_end", self, is_optional=False)
        self.form_layout.insertWidget(self.form_layout.count() - 1, self.vty_range)

        self.add_field("ip_address", IPAddressField("IP Address:", is_optional=True))
        self.add_field("subnet_mask", SubnetMaskField("Subnet Mask:", is_optional=True))

        self.fields["login_password"].radio.setEnabled(False)
        self.fields["subnet_mask"].radio.setEnabled(False)

        self.fields["login_username"].radio.toggled.connect(self._sync_login_password_state)
        self.fields["login_username"].radio.toggled.connect(self._sync_privilege_state)
        self.fields["ip_address"].radio.toggled.connect(self._sync_subnet_mask_state)

        self.fields["login_method"].input_widget.currentTextChanged.connect(self._on_login_method_changed)

        self._sync_login_password_state(self.fields["login_username"].radio.isChecked())
        self._sync_privilege_state(self.fields["login_username"].radio.isChecked())
        self._sync_subnet_mask_state(self.fields["ip_address"].radio.isChecked())
        self._on_login_method_changed(self.fields["login_method"].get_value())

    def _sync_login_password_state(self, checked: bool):
        """
        Synchronizes the state of the login password field with the login username field.
        """
        self.fields["login_password"].input_widget.setEnabled(checked)
        self.fields["login_password"].radio.setChecked(checked)
        if not checked:
            self.fields["login_password"].input_widget.clear()

    def _sync_subnet_mask_state(self, checked: bool):
        """
        Synchronizes the state of the subnet mask field with the IP address field.
        """
        self.fields["subnet_mask"].input_widget.setEnabled(checked)
        self.fields["subnet_mask"].radio.setChecked(checked)
        if not checked:
            self.fields["subnet_mask"].input_widget.clear()

    def _sync_privilege_state(self, checked: bool):
        """
        Enables or disables the entire privilege field based on the username field's state.
        """
        self.fields["login_privilege"].radio.setEnabled(checked)
        self.fields["login_privilege"].input_widget.setEnabled(checked)
        if not checked:
            self.fields["login_privilege"].radio.setChecked(False)
            self.fields["login_privilege"].input_widget.clear()

    def _on_login_method_changed(self, method: str):
        """
        Adjusts the visibility of the line password and local credentials based on the selected login method.
        """
        is_login = method == "login"
        is_local = method == "login local"

        self.fields["line_password"].setVisible(is_login)

        self.fields["login_username"].setVisible(is_local)
        self.fields["login_password"].setVisible(is_local)
        self.fields["login_privilege"].setVisible(is_local)

    def get_data(self) -> dict:
        """
        Retrieves Telnet VTY and interface configuration data.
        """
        vty_start = self.vty_range.start_field.text()
        vty_end = self.vty_range.end_field.text()

        login_user_enabled = self.fields["login_username"].radio.isChecked()
        ip_enabled = self.fields["ip_address"].radio.isChecked()

        return {
            "type": "telnet_connection",
            "interface": self.fields["interface"].get_value(),
            "vty_start": vty_start,
            "vty_end": vty_end,
            "vty_enabled": bool(vty_start.strip() and vty_end.strip()),
            "login_method": self.fields["login_method"].get_value(),
            "line_password": self.fields["line_password"].get_value() if self.fields["line_password"].radio.isChecked() else "",
            "login_username": self.fields["login_username"].get_value() if login_user_enabled else "",
            "login_password": self.fields["login_password"].get_value() if login_user_enabled else "",
            "login_privilege": self.fields["login_privilege"].get_value() if self.fields["login_privilege"].radio.isChecked() else "",
            "ip_address": self.fields["ip_address"].get_value() if ip_enabled else "",
            "subnet_mask": self.fields["subnet_mask"].get_value() if ip_enabled else "",
            "_save_configuration": self.save_configuration_cb.isChecked()
        }

    def update_interfaces(self, interfaces: list[str]):
        """
        Populates the interface dropdown with retrieved device data.
        """
        self.interface_dropdown.input_widget.clear()
        self.interface_dropdown.input_widget.addItems(interfaces)

    def validate_all(self) -> bool:
        """
        Performs validation on standard fields and the VTY range.
        """
        return super().validate_all() and self.vty_range.validate()


class TelnetLoginView(BaseConfigView):
    """
    View handling local user credentials for Telnet access.
    """

    def __init__(self):
        """
        Initializes mandatory login name, privilege, and password fields, and the save configuration toggle.
        """
        super().__init__()

        self.add_field("login_name", BaseInputField("Username:", is_optional=False))
        self.add_field("privilege", RangedNumberField("Privilege (0-15):", 0, 15, is_optional=False))
        self.add_field("login_password", PasswordField("Password:", is_optional=False))

    def get_data(self) -> dict:
        """
        Retrieves Telnet authentication data and the save configuration flag.
        """
        return {
            "type": "telnet_login",
            "login_name": self.fields["login_name"].get_value(),
            "privilege": self.fields["privilege"].get_value(),
            "login_password": self.fields["login_password"].get_value(),
            "_save_configuration": self.save_configuration_cb.isChecked()
        }


class TelnetView:
    """
    Container aggregating independent Telnet configuration sections for routers.
    """

    def __init__(self):
        """
        Instantiates specific Telnet configuration views.
        """
        self.connection_section = TelnetConnectionView()
        self.login_section = TelnetLoginView()