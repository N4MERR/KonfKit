"""
Provides the model for generating SSH configuration commands.
"""
from model.device_configuration_models.base_config_model import BaseConfigModel


class SSHModel(BaseConfigModel):
    """
    Model handling the generation of IOS commands for SSH device management.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Translates raw input data into a sequence of executable IOS SSH commands.
        """
        commands = []
        if kwargs.get("domain"):
            commands.append(f"ip domain-name {kwargs['domain']}")

        if kwargs.get("rsa_size"):
            commands.append(f"crypto key generate rsa modulus {kwargs['rsa_size']}")

        if kwargs.get("username") and kwargs.get("password"):
            commands.append(f"username {kwargs['username']} privilege 15 secret {kwargs['password']}")

        commands.append("ip ssh version 2")

        commands.append(f"line vty {kwargs.get('vty_start', '0')} {kwargs.get('vty_end', '4')}")
        commands.append("transport input ssh")

        if kwargs.get("local_login"):
            commands.append("login local")
        else:
            commands.append("login")

        return commands