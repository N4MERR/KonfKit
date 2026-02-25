"""
Models for generating Cisco IOS commands for Telnet subsections.
"""
from model.device_configuration_models.base_config_model import BaseConfigModel

class TelnetAuthModel(BaseConfigModel):
    """
    Model for generating Telnet local user commands.
    """
    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates commands for username and password.
        """
        commands = ["configure terminal"]
        if kwargs.get('login_name') and kwargs.get('login_password'):
            commands.append(f"username {kwargs.get('login_name')} password {kwargs.get('login_password')}")
        return commands if len(commands) > 1 else []

class TelnetVtyModel(BaseConfigModel):
    """
    Model for generating VTY line commands for Telnet.
    """
    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates commands for line range, local login, and transport.
        """
        commands = ["configure terminal"]
        if kwargs.get('vty_enabled'):
            commands.append(f"line vty {kwargs.get('vty_start')} {kwargs.get('vty_end')}")
            commands.append("login local")
            commands.append("transport input telnet")
            commands.append("exit")
        return commands if len(commands) > 1 else []