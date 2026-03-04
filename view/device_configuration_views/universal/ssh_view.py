from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.config_fields.base_config_field import BaseConfigField
from view.device_configuration_views.config_fields.dropdown_field import DropdownField
from view.device_configuration_views.config_fields.password_field import PasswordField
from view.device_configuration_views.config_fields.password_confirm_field import PasswordConfirmField
from view.device_configuration_views.config_fields.ranged_number_field import RangedNumberField
from view.device_configuration_views.config_fields.range_field import RangeField

class SSHConnectionSection(BaseConfigView):
    """
    View handling global SSH parameters like hostname, domain, RSA keys, protocol version, and VTY lines.
    """

    def __init__(self):
        """
        Initializes global SSH configuration fields with strict input validation and a write memory toggle.
        """
        super().__init__()

        self.add_field("hostname", BaseConfigField("Hostname:", is_optional=False))
        self.add_field("domain_name", BaseConfigField("Domain Name:", is_optional=False))
        self.add_field("rsa_modulus", DropdownField("RSA Key Modulus:", ["1024", "2048", "4096"], is_optional=False))
        self.add_field("ssh_version", DropdownField("SSH Version:", ["2", "1"], is_optional=False))
        self.add_field("ssh_timeout", RangedNumberField("SSH Timeout (1-120 seconds):", 1, 120, is_optional=True))
        self.add_field("ssh_retries", RangedNumberField("Authentication Retries (1-5):", 1, 5, is_optional=True))

        self.vty_range = RangeField("VTY Line Range:", "vty_start", "vty_end", self, is_optional=False)
        self.form_layout.insertWidget(self.form_layout.count() - 1, self.vty_range)

    def get_data(self) -> dict:
        """
        Retrieves data for global SSH settings including optional field states and the write memory flag.
        """
        return {
            "type": "ssh_global",
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
            "_write_memory": self.write_memory_cb.isChecked()
        }

    def validate_all(self) -> bool:
        """
        Performs validation on standard view fields and the specialized VTY range field.
        """
        return super().validate_all() and self.vty_range.validate()

class SSHLoginSection(BaseConfigView):
    """
    View handling mandatory local SSH user authentication setup.
    """

    def __init__(self):
        """
        Initializes login name, password, and password confirmation fields along with a write memory toggle.
        """
        super().__init__()

        self.add_field("login_name", BaseConfigField("Username:", is_optional=False))
        self.add_field("privilege", RangedNumberField("Privilege (0-15):", 0, 15, is_optional=False))
        pwd_field = self.add_field("login_password", PasswordField("Password:", is_optional=False))
        self.add_field("login_password_confirm",
                       PasswordConfirmField("Confirm Password:", pwd_field, is_optional=False))

    def get_data(self) -> dict:
        """
        Retrieves local authentication data and the write memory flag.
        """
        return {
            "type": "ssh_auth",
            "login_name": self.fields["login_name"].get_value(),
            "privilege": self.fields["privilege"].get_value(),
            "login_password": self.fields["login_password"].get_value(),
            "_write_memory": self.write_memory_cb.isChecked()
        }

class SSHView:
    """
    Container aggregating independent SSH configuration sections.
    """

    def __init__(self):
        """
        Instantiates specific SSH configuration views.
        """
        self.global_section = SSHConnectionSection()
        self.auth_section = SSHLoginSection()