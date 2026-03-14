from view.device_configuration_views.input_fields.base_input_field import BaseInputField
from view.device_configuration_views.input_fields.ip_address_field import IPAddressField
from view.device_configuration_views.input_fields.password_field import PasswordField
from view.device_configuration_views.input_fields.dropdown_field import DropdownField
from .base_connection_dialog import BaseConnectionDialog


class TelnetConnectionDialog(BaseConnectionDialog):
    """
    Dialog for configuring a Telnet connection with a dynamic authentication mode selector.
    """

    def __init__(self, parent=None):
        """
        Initializes the Telnet configuration dialog.
        """
        super().__init__("Add Telnet Connection", parent)

    def _add_specific_fields(self):
        """
        Injects network settings and the authentication mode selector.
        """
        self.ip_input = IPAddressField("IP Address:", is_optional=False)
        self.port_input = BaseInputField("Telnet Port:", is_optional=False)
        self.port_input.input_widget.setText("23")

        self.auth_mode = DropdownField("Auth Mode:", ["No Login", "Login", "Login Local"], is_optional=False)
        self.auth_mode.input_widget.currentTextChanged.connect(self._update_auth_fields)

        self.add_field(self.ip_input)
        self.add_field(self.port_input)
        self.add_field(self.auth_mode)

        self.user_input = BaseInputField("Login Username:", is_optional=False)
        self.pass_input = PasswordField("Login Password:", is_optional=False)
        self.enable_pass_input = PasswordField("Enable Password:", is_optional=False)

        self.add_field(self.user_input)
        self.add_field(self.pass_input)
        self.add_field(self.enable_pass_input)

        self._update_auth_fields()

    def _update_auth_fields(self):
        """
        Toggles visibility of credential fields based on the selected authentication mode.
        """
        mode = self.auth_mode.get_value()

        self.user_input.setVisible(mode == "Login Local")
        self.pass_input.setVisible(mode in ["Login", "Login Local"])
        self.enable_pass_input.setVisible(True)

    def get_data(self):
        """
        Extracts validated input data and maps them to standard Netmiko parameters.
        """
        mode = self.auth_mode.get_value()

        username = self.user_input.get_value() if mode == "Login Local" else ""
        password = self.pass_input.get_value() if mode in ["Login", "Login Local"] else ""

        port_val = self.port_input.get_value()
        port = int(port_val) if port_val else 23

        return {
            "name": self.name_input.get_value(),
            "device_type": "cisco_ios_telnet",
            "host": self.ip_input.get_value(),
            "port": port,
            "username": username,
            "password": password,
            "secret": self.enable_pass_input.get_value()
        }