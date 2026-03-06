from model.device_configuration_models.base_config_model import BaseConfigModel


class TelnetConnectionModel(BaseConfigModel):
    """
    Model for generating VTY line commands for Telnet.
    """

    def generate_commands(self, **data) -> list[str]:
        """
        Generates commands for line range and transport.
        """
        commands = []
        write_memory = data.pop("_write_memory", False)

        if data.get("vty_enabled"):
            commands.append(f"line vty {data.get('vty_start')} {data.get('vty_end')}")
            commands.append("login local")
            commands.append("transport input telnet")
            commands.append("exit")

        if write_memory:
            commands.append("do write memory")

        return commands


class TelnetLoginModel(BaseConfigModel):
    """
    Model for generating Telnet local user commands.
    """

    def generate_commands(self, **data) -> list[str]:
        """
        Generates commands for username, privilege, password, and local login enforcement.
        """
        commands = []
        write_memory = data.pop("_write_memory", False)

        if data.get("login_name") and data.get("login_password"):
            privilege = data.get("privilege")
            commands.append(f"username {data.get('login_name')} privilege {privilege} secret {data.get('login_password')}")
            commands.append("exit")

        if write_memory:
            commands.append("do write memory")

        return commands


class TelnetModel:
    """
    Wrapper model aggregating independent Telnet configuration models.
    """

    def __init__(self, session_manager):
        """
        Instantiates specific Telnet configuration models.
        """
        self.connection_section = TelnetConnectionModel(session_manager)
        self.login_section = TelnetLoginModel(session_manager)