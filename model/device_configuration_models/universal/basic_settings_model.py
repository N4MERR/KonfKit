from model.device_configuration_models.base_config_model import BaseConfigModel

class BasicSettingsModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for basic device settings.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates Cisco CLI commands for hostname, secret, and banner based on enabled fields.
        """
        commands = ["configure terminal"]

        if kwargs.get('hostname_enabled') and kwargs.get('hostname'):
            commands.append(f"hostname {kwargs.get('hostname')}")

        if kwargs.get('domain_name_enabled') and kwargs.get('domain_name'):
            commands.append(f"ip domain-name {kwargs.get('domain_name')}")

        if kwargs.get('enable_password_enabled') and kwargs.get('enable_password'):
            commands.append(f"enable password {kwargs.get('enable_password')}")

        if kwargs.get('enable_secret_enabled') and kwargs.get('enable_secret'):
            commands.append(f"enable secret {kwargs.get('enable_secret')}")

        if kwargs.get('banner_motd_enabled') and kwargs.get('banner_motd'):
            commands.append(f"banner motd ^{kwargs.get('banner_motd')}^")

        if kwargs.get('password_encryption_enabled'):
            commands.append("service password-encryption")

        return commands if len(commands) > 1 else []