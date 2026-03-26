from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.input_fields.string_input_field import StringInputField
from view.device_configuration_views.input_fields.password_field import PasswordField
from view.device_configuration_views.input_fields.multiline_field import MultilineField
from view.device_configuration_views.input_fields.radio_indicator_field import RadioIndicatorField

class SystemSettingsView(BaseConfigView):
    """
    View for basic device configuration like hostname and domain name incorporating memory writing options.
    """

    def __init__(self):
        """
        Initializes basic settings fields and embeds the save configuration toggle into the layout.
        """
        super().__init__()
        self.add_field("hostname", StringInputField("Hostname:", max_length=63, allowed_chars="a-zA-Z0-9-", start_with="a-zA-Z", is_optional=True))
        self.add_field("domain_name", StringInputField("Domain Name:", max_length=253, allowed_chars="a-zA-Z0-9.-", start_with="a-zA-Z0-9", is_optional=True))

        enable_sec = self.add_field("enable_secret", PasswordField("Enable Secret:", is_optional=True))

        self.password_encryption = RadioIndicatorField("Enable Service Password-Encryption")
        self.form_layout.insertWidget(self.form_layout.count() - 1, self.password_encryption)

        self.add_field("banner_motd", MultilineField("Banner MOTD:", is_optional=True))

    def get_data(self) -> dict:
        """
        Retrieves data for basic settings based on active radio indicators and the save configuration flag.
        """
        return {
            "type": "basic_settings",
            "hostname": self.fields["hostname"].get_value(),
            "hostname_enabled": self.fields["hostname"].radio.isChecked(),
            "domain_name": self.fields["domain_name"].get_value(),
            "domain_name_enabled": self.fields["domain_name"].radio.isChecked(),
            "enable_secret": self.fields["enable_secret"].get_value(),
            "enable_secret_enabled": self.fields["enable_secret"].radio.isChecked(),
            "banner_motd": self.fields["banner_motd"].get_value(),
            "banner_motd_enabled": self.fields["banner_motd"].radio.isChecked(),
            "password_encryption_enabled": self.password_encryption.isChecked(),
            "_save_configuration": self.save_configuration_cb.isChecked()
        }