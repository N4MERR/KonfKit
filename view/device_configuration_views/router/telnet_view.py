from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.input_fields.base_input_field import BaseInputField
from view.device_configuration_views.input_fields.password_field import PasswordField
from view.device_configuration_views.input_fields.password_confirm_field import PasswordConfirmField
from view.device_configuration_views.input_fields.ranged_number_field import RangedNumberField
from view.device_configuration_views.input_fields.range_field import RangeField
from view.device_configuration_views.input_fields.dropdown_field import DropdownField


class TelnetConnectionView(BaseConfigView):
    """
    View handling line transport and VTY lines for Telnet.
    """

    def __init__(self):
        """
        Initializes VTY range fields, login method, and the write memory toggle.
        """
        super().__init__()

        self.add_field("login_method", DropdownField("Login Method:", ["login local", "login"], is_optional=False))

        self.vty_range = RangeField("VTY Line Range:", "vty_start", "vty_end", self, is_optional=False)
        self.form_layout.insertWidget(self.form_layout.count() - 1, self.vty_range)

    def get_data(self) -> dict:
        """
        Retrieves Telnet VTY configuration data and the write memory flag.
        """
        vty_start = self.vty_range.start_field.text()
        vty_end = self.vty_range.end_field.text()

        return {
            "type": "telnet_connection",
            "vty_start": vty_start,
            "vty_end": vty_end,
            "vty_enabled": bool(vty_start.strip() and vty_end.strip()),
            "login_method": self.fields["login_method"].get_value(),
            "_write_memory": self.write_memory_cb.isChecked()
        }

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
        Initializes mandatory login name, privilege, password fields, and the write memory toggle.
        """
        super().__init__()

        self.add_field("login_name", BaseInputField("Username:", is_optional=False))
        self.add_field("privilege", RangedNumberField("Privilege (0-15):", 0, 15, is_optional=False))
        pwd_field = self.add_field("login_password", PasswordField("Password:", is_optional=False))
        self.add_field("login_password_confirm",
                       PasswordConfirmField("Confirm Password:", pwd_field, is_optional=False))

    def get_data(self) -> dict:
        """
        Retrieves Telnet authentication data and the write memory flag.
        """
        return {
            "type": "telnet_login",
            "login_name": self.fields["login_name"].get_value(),
            "privilege": self.fields["privilege"].get_value(),
            "login_password": self.fields["login_password"].get_value(),
            "_write_memory": self.write_memory_cb.isChecked()
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