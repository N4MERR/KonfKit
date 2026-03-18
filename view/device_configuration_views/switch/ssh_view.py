from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.input_fields.base_input_field import BaseInputField
from view.device_configuration_views.input_fields.dropdown_field import DropdownField
from view.device_configuration_views.input_fields.password_field import PasswordField
from view.device_configuration_views.input_fields.ranged_number_field import RangedNumberField
from view.device_configuration_views.input_fields.range_field import RangeField
from view.device_configuration_views.input_fields.ip_address_field import IPAddressField
from view.device_configuration_views.input_fields.subnet_mask_field import SubnetMaskField
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal


class SSHConnectionView(BaseConfigView):
    """
    View handling global SSH parameters and specific VLAN/SVI assignments for switches.
    """
    load_interfaces_signal = Signal()

    def __init__(self):
        """
        Initializes switch-specific SSH configuration fields with strict input validation.
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
        self.add_field("management_interface", self.interface_dropdown)

        self.add_field("vlan_id", RangedNumberField("VLAN ID:", 1, 4094, is_optional=False))
        self.add_field("ip_address", IPAddressField("IP Address:", is_optional=True))
        self.add_field("subnet_mask", SubnetMaskField("Subnet Mask:", is_optional=True))
        self.add_field("default_gateway", IPAddressField("Default Gateway:", is_optional=True))

        self.fields["subnet_mask"].radio.setEnabled(False)
        self.fields["ip_address"].radio.toggled.connect(self._sync_subnet_mask_state)

        self.add_field("hostname", BaseInputField("Hostname:", is_optional=False))
        self.add_field("domain_name", BaseInputField("Domain Name:", is_optional=False))
        self.add_field("rsa_modulus", DropdownField("RSA Key Modulus:", ["1024", "2048", "4096"], is_optional=False))
        self.add_field("ssh_version", DropdownField("SSH Version:", ["2", "1"], is_optional=False))
        self.add_field("ssh_timeout", RangedNumberField("SSH Timeout (1-120 seconds):", 1, 120, is_optional=True))
        self.add_field("ssh_retries", RangedNumberField("Authentication Retries (1-5):", 1, 5, is_optional=True))

        self.vty_range = RangeField("VTY Line Range:", "vty_start", "vty_end", self, is_optional=False)
        self.form_layout.insertWidget(self.form_layout.count() - 1, self.vty_range)

        self._sync_subnet_mask_state(self.fields["ip_address"].radio.isChecked())

    def _sync_subnet_mask_state(self, checked: bool):
        """
        Synchronizes the state of the subnet mask field with the IP address field.
        """
        self.fields["subnet_mask"].input_widget.setEnabled(checked)
        self.fields["subnet_mask"].radio.setChecked(checked)
        if not checked:
            self.fields["subnet_mask"].input_widget.clear()

    def update_interfaces(self, interfaces: list[str]):
        """
        Populates the interface dropdown with retrieved device data.
        """
        self.interface_dropdown.input_widget.clear()
        self.interface_dropdown.input_widget.addItems(interfaces)

    def get_data(self) -> dict:
        """
        Retrieves data for global SSH settings, VLAN configuration, and SVI properties.
        """
        ip_enabled = self.fields["ip_address"].radio.isChecked()

        return {
            "type": "ssh_global_switch",
            "management_interface": self.fields["management_interface"].get_value(),
            "vlan_id": self.fields["vlan_id"].get_value(),
            "ip_address": self.fields["ip_address"].get_value() if ip_enabled else "",
            "subnet_mask": self.fields["subnet_mask"].get_value() if ip_enabled else "",
            "default_gateway": self.fields["default_gateway"].get_value() if self.fields["default_gateway"].radio.isChecked() else "",
            "hostname": self.fields["hostname"].get_value(),
            "domain_name": self.fields["domain_name"].get_value(),
            "rsa_modulus": self.fields["rsa_modulus"].get_value(),
            "ssh_version": self.fields["ssh_version"].get_value(),
            "ssh_timeout": self.fields["ssh_timeout"].get_value(),
            "ssh_timeout_enabled": self.fields["ssh_timeout"].radio.isChecked(),
            "ssh_retries": self.fields["ssh_retries"].get_value(),
            "ssh_retries_enabled": self.fields["ssh_retries"].radio.isChecked(),
            "vty_start": self.vty_range.start_field.text(),
            "vty_end": self.vty_range.end_field.text(),
            "vty_enabled": bool(self.vty_range.start_field.text().strip() and self.vty_range.end_field.text().strip()),
            "_save_configuration": self.save_configuration_cb.isChecked()
        }

    def validate_all(self) -> bool:
        """
        Performs validation on standard view fields and the specialized VTY range field.
        """
        return super().validate_all() and self.vty_range.validate()


class SSHAuthenticationView(BaseConfigView):
    """
    View handling mandatory local SSH user authentication setup.
    """

    def __init__(self):
        """
        Initializes authentication name and password fields along with a save configuration toggle.
        """
        super().__init__()

        self.add_field("login_name", BaseInputField("Username:", is_optional=False))
        self.add_field("privilege", RangedNumberField("Privilege (0-15):", 0, 15, is_optional=True))
        self.add_field("login_password", PasswordField("Password:", is_optional=False))

    def get_data(self) -> dict:
        """
        Retrieves local authentication data and the save configuration flag.
        """
        return {
            "type": "ssh_auth",
            "login_name": self.fields["login_name"].get_value(),
            "privilege": self.fields["privilege"].get_value() if self.fields["privilege"].radio.isChecked() else None,
            "login_password": self.fields["login_password"].get_value(),
            "_save_configuration": self.save_configuration_cb.isChecked()
        }


class SSHView:
    """
    Container aggregating independent SSH configuration sections for switches.
    """

    def __init__(self):
        """
        Instantiates specific SSH configuration views for switches.
        """
        self.global_section = SSHConnectionView()
        self.auth_section = SSHAuthenticationView()