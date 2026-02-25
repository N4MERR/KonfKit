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

        if kwargs.get('secret_enabled') and kwargs.get('secret'):
            commands.append(f"enable secret {kwargs.get('secret')}")

        if kwargs.get('banner_enabled') and kwargs.get('banner'):
            commands.append(f"banner motd ^{kwargs.get('banner')}^")

        return commands if len(commands) > 1 else []