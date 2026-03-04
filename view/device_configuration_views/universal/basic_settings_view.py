from PySide6.QtWidgets import QCheckBox
from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.config_fields.base_config_field import BaseConfigField
from view.device_configuration_views.config_fields.password_field import PasswordField
from view.device_configuration_views.config_fields.password_confirm_field import PasswordConfirmField
from view.device_configuration_views.config_fields.multiline_field import MultilineField
from view.device_configuration_views.config_fields.radio_indicator_field import RadioIndicatorField

class BasicSettingsView(BaseConfigView):
    """
    View for basic device configuration like hostname and domain name incorporating memory writing options.
    """

    def __init__(self):
        """
        Initializes basic settings fields and embeds the write memory toggle into the layout.
        """
        super().__init__()
        self.add_field("hostname", BaseConfigField("Hostname:", is_optional=True))
        self.add_field("domain_name", BaseConfigField("Domain Name:", is_optional=True))

        enable_pwd = self.add_field("enable_password", PasswordField("Enable Password:", is_optional=True))
        self.add_field("confirm_password", PasswordConfirmField("Confirm Password:", enable_pwd))

        enable_sec = self.add_field("enable_secret", PasswordField("Enable Secret:", is_optional=True))
        self.add_field("confirm_secret", PasswordConfirmField("Confirm Secret:", enable_sec))

        self.password_encryption = RadioIndicatorField("Enable Service Password-Encryption")
        self.form_layout.insertWidget(self.form_layout.count() - 1, self.password_encryption)

        self.add_field("banner_motd", MultilineField("Banner MOTD:", is_optional=True))

        self.write_memory_cb = QCheckBox("Write Memory")
        self.button_layout.insertWidget(0, self.write_memory_cb)

    def get_data(self) -> dict:
        """
        Retrieves data for basic settings based on active radio indicators and the write memory flag.
        """
        return {
            "type": "basic_settings",
            "hostname": self.fields["hostname"].get_value(),
            "hostname_enabled": self.fields["hostname"].radio.isChecked(),
            "domain_name": self.fields["domain_name"].get_value(),
            "domain_name_enabled": self.fields["domain_name"].radio.isChecked(),
            "enable_password": self.fields["enable_password"].get_value(),
            "enable_password_enabled": self.fields["enable_password"].radio.isChecked(),
            "enable_secret": self.fields["enable_secret"].get_value(),
            "enable_secret_enabled": self.fields["enable_secret"].radio.isChecked(),
            "banner_motd": self.fields["banner_motd"].get_value(),
            "banner_motd_enabled": self.fields["banner_motd"].radio.isChecked(),
            "password_encryption_enabled": self.password_encryption.isChecked(),
            "_write_memory": self.write_memory_cb.isChecked()
        }