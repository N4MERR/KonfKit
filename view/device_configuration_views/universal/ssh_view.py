"""
SSH configuration views updated to match the existing UI style of OSPF and Basic Settings.
"""
from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.config_fields import (
    BaseConfigField, NumberField, DropdownField, PasswordField, RangeField
)


class SSHGlobalSection(BaseConfigView):
    """
    View handling global SSH parameters like domain, RSA keys, and protocol version.
    """

    def __init__(self):
        """
        Initializes global SSH configuration fields including version selection.
        """
        super().__init__()

        domain = self.add_field("domain_name", BaseConfigField("Domain Name:"))
        domain.set_error_message("Domain name cannot be empty.")

        self.add_field("key_size", DropdownField("RSA Key Size:", ["512", "1024", "2048", "4096"]))

        self.add_field("ssh_version", DropdownField("SSH Version:", ["1", "2"]))

        timeout = self.add_field("timeout", NumberField("Timeout (seconds):"))
        timeout.set_error_message("Timeout must be a valid number.")

        retries = self.add_field("retries", NumberField("Authentication Retries:"))
        retries.set_error_message("Retries must be a valid number.")

    def get_data(self) -> dict:
        """
        Retrieves data for global SSH settings using radio indicators.
        """
        return {
            "type": "ssh_global",
            "domain_name": self.fields["domain_name"].get_value(),
            "domain_name_enabled": self.fields["domain_name"].radio.isChecked(),
            "key_size": self.fields["key_size"].get_value(),
            "key_size_enabled": self.fields["key_size"].radio.isChecked(),
            "ssh_version": self.fields["ssh_version"].get_value(),
            "ssh_version_enabled": self.fields["ssh_version"].radio.isChecked(),
            "timeout": self.fields["timeout"].get_value(),
            "timeout_enabled": self.fields["timeout"].radio.isChecked(),
            "retries": self.fields["retries"].get_value(),
            "retries_enabled": self.fields["retries"].radio.isChecked()
        }


class SSHAuthSection(BaseConfigView):
    """
    View handling mandatory local SSH user authentication.
    """

    def __init__(self):
        """
        Initializes mandatory login name and password fields.
        """
        super().__init__()

        login_name = self.add_field("login_name", BaseConfigField("Login Name:", is_optional=False))
        login_name.set_error_message("Login name is required.")

        login_pwd = self.add_field("login_password", PasswordField("Login Password:", is_optional=False))
        login_pwd.set_error_message("Login password is required.")

    def get_data(self) -> dict:
        """
        Retrieves local authentication data.
        """
        return {
            "type": "ssh_auth",
            "login_name": self.fields["login_name"].get_value(),
            "login_password": self.fields["login_password"].get_value()
        }


class SSHVtySection(BaseConfigView):
    """
    View handling SSH access configuration for VTY lines.
    """

    def __init__(self):
        """
        Initializes VTY range fields.
        """
        super().__init__()
        self.vty_range = RangeField("VTY Line Range:", "vty_start", "vty_end", self)
        self.form_layout.insertWidget(self.form_layout.count() - 1, self.vty_range)

    def get_data(self) -> dict:
        """
        Retrieves VTY line configuration data.
        """
        return {
            "type": "ssh_vty",
            "vty_start": self.vty_range.start_field.text(),
            "vty_end": self.vty_range.end_field.text(),
            "vty_enabled": bool(self.vty_range.start_field.text().strip() and self.vty_range.end_field.text().strip())
        }

    def validate_all(self) -> bool:
        """
        Performs validation on standard fields and the VTY range.
        """
        return super().validate_all() and self.vty_range.validate()


class SSHView:
    """
    Container aggregating independent SSH configuration sections.
    """

    def __init__(self):
        """
        Instantiates specific SSH configuration views.
        """
        self.global_section = SSHGlobalSection()
        self.auth_section = SSHAuthSection()
        self.vty_section = SSHVtySection()