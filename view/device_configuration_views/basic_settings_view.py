from PySide6.QtCore import Signal
from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.config_fields import (
    BaseConfigField, PasswordField, PasswordConfirmField, MultilineField
)

class BasicSettingsView(BaseConfigView):
    """
    Basic settings view implementing specific library fields.
    """

    def __init__(self):
        """
        Initializes the view and registers fields. Connections are handled by the base class.
        """
        super().__init__()

        hostname = self.add_field("hostname", BaseConfigField("Hostname:", is_optional=True))
        hostname.set_error_message("Hostname cannot be empty if enabled.")

        secret = self.add_field("secret", PasswordField("Enable Secret:", is_optional=True))
        secret.set_error_message("Secret is required if enabled.")

        confirm = self.add_field("confirm_secret", PasswordConfirmField("Confirm Secret:", secret))
        confirm.set_error_message("Passwords do not match.")

        banner = self.add_field("banner", MultilineField("Banner MOTD:", is_optional=True))
        banner.set_error_message("Banner content is required if enabled.")

    def get_data(self):
        """
        Overrides base get_data to provide the specific keys required by the BasicSettingsModel.
        """
        return {
            "hostname": self.fields["hostname"].get_value(),
            "hostname_enabled": self.fields["hostname"].checkbox.isChecked(),
            "secret": self.fields["secret"].get_value(),
            "secret_enabled": self.fields["secret"].checkbox.isChecked(),
            "confirm_secret": self.fields["confirm_secret"].get_value(),
            "banner": self.fields["banner"].get_value(),
            "banner_enabled": self.fields["banner"].checkbox.isChecked()
        }