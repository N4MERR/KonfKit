from PySide6.QtWidgets import QCheckBox
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
        Initializes mandatory login name, password fields, and the write memory toggle.
        """
        super().__init__()

        self.add_field("login_name", BaseConfigField("Login Name:", is_optional=False))
        self.add_field("login_password", PasswordField("Login Password:", is_optional=False))

        self.write_memory_cb = QCheckBox("Write Memory")
        self.button_layout.insertWidget(0, self.write_memory_cb)

    def get_data(self) -> dict:
        """
        Retrieves Telnet authentication data and the write memory flag.
        """
        return {
            "type": "telnet_auth",
            "login_name": self.fields["login_name"].get_value(),
            "login_password": self.fields["login_password"].get_value(),
            "_write_memory": self.write_memory_cb.isChecked()
        }


class TelnetVtySection(BaseConfigView):
    """
    View handling line transport and protocol for Telnet.
    """

    def __init__(self):
        """
        Initializes VTY range fields for Telnet access and the write memory toggle.
        """
        super().__init__()

        self.vty_range = RangeField("VTY Line Range:", "vty_start", "vty_end", self)
        self.form_layout.insertWidget(self.form_layout.count() - 1, self.vty_range)

        self.write_memory_cb = QCheckBox("Write Memory")
        self.button_layout.insertWidget(0, self.write_memory_cb)

    def get_data(self) -> dict:
        """
        Retrieves Telnet VTY configuration data and the write memory flag.
        """
        return {
            "type": "telnet_vty",
            "vty_start": self.vty_range.start_field.text(),
            "vty_end": self.vty_range.end_field.text(),
            "vty_enabled": bool(self.vty_range.start_field.text().strip() and self.vty_range.end_field.text().strip()),
            "_write_memory": self.write_memory_cb.isChecked()
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