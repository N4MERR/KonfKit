from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.config_fields import PasswordField, NumberField

class TelnetView(BaseConfigView):
    """
    Telnet configuration view.
    """

    def __init__(self):
        """
        Initializes Telnet configuration fields.
        """
        super().__init__()

        password = self.add_field("password", PasswordField("VTY Password:"))
        password.set_error_message("Password is required for Telnet.")

        self.add_field("first_line", NumberField("First VTY Line:"))
        self.add_field("last_line", NumberField("Last VTY Line:"))

    def get_data(self):
        """
        Returns data for Telnet configuration.
        """
        return {
            "password": self.fields["password"].get_value(),
            "first_line": self.fields["first_line"].get_value(),
            "last_line": self.fields["last_line"].get_value()
        }