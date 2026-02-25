from model.device_configuration_models.base_config_model import BaseConfigModel

class TelnetModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for Telnet configuration.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates Cisco CLI commands for VTY lines and Telnet access based on enabled fields.
        """
        commands = ["configure terminal", "line vty 0 4"]

        if kwargs.get('password_enabled') and kwargs.get('password'):
            commands.append(f"password {kwargs.get('password')}")
            commands.append("login")

        if kwargs.get('transport_enabled'):
            commands.append("transport input telnet")

        return commands if len(commands) > 2 else []