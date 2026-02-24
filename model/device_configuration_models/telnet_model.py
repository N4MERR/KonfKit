"""
Provides the model for generating Telnet configuration commands.
"""
from model.device_configuration_models.base_config_model import BaseConfigModel


class TelnetModel(BaseConfigModel):
    """
    Model handling the generation of IOS commands for Telnet device management.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Translates raw input data into a sequence of executable IOS Telnet commands.
        """
        commands = []
        if kwargs.get("username") and kwargs.get("password"):
            commands.append(f"username {kwargs['username']} privilege 15 secret {kwargs['password']}")

        commands.append(f"line vty {kwargs.get('vty_start', '0')} {kwargs.get('vty_end', '4')}")
        commands.append("transport input telnet")

        if kwargs.get("local_login"):
            commands.append("login local")
        else:
            commands.append("login")

        return commands