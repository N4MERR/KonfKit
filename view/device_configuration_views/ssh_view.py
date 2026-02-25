from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.config_fields import BaseConfigField, NumberField

class SSHView(BaseConfigView):
    """
    SSH configuration view.
    """

    def __init__(self):
        """
        Initializes SSH configuration fields.
        """
        super().__init__()

        domain = self.add_field("domain_name", BaseConfigField("Domain Name:"))
        domain.set_error_message("Domain name is required for SSH.")

        self.add_field("key_size", NumberField("RSA Key Size (512-4096):"))
        self.add_field("version", NumberField("SSH Version (1 or 2):"))
        self.add_field("timeout", NumberField("Timeout (seconds):"))
        self.add_field("retries", NumberField("Authentication Retries:"))

    def get_data(self):
        """
        Returns dictionary of SSH configuration values.
        """
        return {key: field.get_value() for key, field in self.fields.items()}