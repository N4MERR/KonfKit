"""
Telnet configuration views updated to match the existing UI style of OSPF and Basic Settings.
"""
from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.config_fields import (
    BaseConfigField, PasswordField, RangeField
)


class TelnetAuthSection(BaseConfigView):
    """
    View handling local user credentials for Telnet access.
    """

    def __init__(self):
        """
        Initializes mandatory login name and password fields.
        """
        super().__init__()

        login_name = self.add_field("login_name", BaseConfigField("Login Name:", is_optional=False))
        login_name.set_error_message("Login name is required for local authentication.")

        login_pwd = self.add_field("login_password", PasswordField("Login Password:", is_optional=False))
        login_pwd.set_error_message("Login password is required for local authentication.")

    def get_data(self) -> dict:
        """
        Retrieves Telnet authentication data.
        """
        return {
            "type": "telnet_auth",
            "login_name": self.fields["login_name"].get_value(),
            "login_password": self.fields["login_password"].get_value()
        }


class TelnetVtySection(BaseConfigView):
    """
    View handling line transport and protocol for Telnet.
    """

    def __init__(self):
        """
        Initializes VTY range fields for Telnet access.
        """
        super().__init__()
        self.vty_range = RangeField("VTY Line Range:", "vty_start", "vty_end", self)
        self.form_layout.insertWidget(self.form_layout.count() - 1, self.vty_range)

    def get_data(self) -> dict:
        """
        Retrieves Telnet VTY configuration data.
        """
        return {
            "type": "telnet_vty",
            "vty_start": self.vty_range.start_field.text(),
            "vty_end": self.vty_range.end_field.text(),
            "vty_enabled": bool(self.vty_range.start_field.text().strip() and self.vty_range.end_field.text().strip())
        }

    def validate_all(self) -> bool:
        """
        Performs validation on standard fields and the VTY range.
        """
        return super().validate_all() and self.vty_range.validate()


class TelnetView:
    """
    Container aggregating independent Telnet configuration sections.
    """

    def __init__(self):
        """
        Instantiates specific Telnet configuration views.
        """
        self.auth_section = TelnetAuthSection()
        self.vty_section = TelnetVtySection()