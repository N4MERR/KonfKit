from view.device_configuration_views.input_fields.base_input_field import BaseInputField
from view.device_configuration_views.input_fields.ip_address_field import IPAddressField
from view.device_configuration_views.input_fields.password_field import PasswordField
from .base_connection_dialog import BaseConnectionDialog


class SSHConnectionDialog(BaseConnectionDialog):
    """
    Dialog for configuring an SSH connection using inline-validated input fields.
    """

    def __init__(self, parent=None):
        """
        Initializes the SSH configuration dialog.
        """
        super().__init__("Add SSH Connection", parent)

    def _add_specific_fields(self):
        """
        Injects IP, Port, Username, Login Password, and Enable Password fields.
        """
        self.ip_input = IPAddressField("IP Address:", is_optional=False)

        self.port_input = BaseInputField("SSH Port:", is_optional=False)
        self.port_input.input_widget.setText("22")

        self.user_input = BaseInputField("Login Username:", is_optional=False)
        self.pass_input = PasswordField("Login Password:", is_optional=False)
        self.enable_pass_input = PasswordField("Enable Password:", is_optional=False)

        self.add_field(self.ip_input)
        self.add_field(self.port_input)
        self.add_field(self.user_input)
        self.add_field(self.pass_input)
        self.add_field(self.enable_pass_input)

    def get_data(self):
        """
        Extracts validated input data into a dictionary suitable for Netmiko connections.
        """
        port_val = self.port_input.get_value()
        port = int(port_val) if port_val else 22

        return {
            "name": self.name_input.get_value(),
            "device_type": "cisco_ios",
            "host": self.ip_input.get_value(),
            "port": port,
            "username": self.user_input.get_value(),
            "password": self.pass_input.get_value(),
            "secret": self.enable_pass_input.get_value()
        }