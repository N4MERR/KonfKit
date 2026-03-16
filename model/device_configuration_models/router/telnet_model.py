from model.device_configuration_models.base_config_model import BaseConfigModel


class TelnetConnectionModel(BaseConfigModel):
    """
    Model for generating VTY line commands for Telnet.
    """

    def generate_commands(self, **data) -> list[str]:
        """
        Generates commands for line range, transport, and login method.
        """
        commands = []

        vty_enabled = data.get("vty_enabled", False)
        if vty_enabled:
            vty_start = str(data.get('vty_start', '')).strip()
            vty_end = str(data.get('vty_end', '')).strip()
            login_method = str(data.get('login_method', 'login local')).strip()

            commands.append(f"line vty {vty_start} {vty_end}")
            commands.append(login_method)
            commands.append("transport input telnet")
            commands.append("exit")

        commands.extend(super().generate_commands(**data))
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

        login_name = str(data.get("login_name", "")).strip()
        login_password = str(data.get("login_password", "")).strip()

        if login_name and login_password:
            privilege = str(data.get("privilege", "15")).strip()
            commands.append(f"username {login_name} privilege {privilege} secret {login_password}")
            commands.append("exit")

        commands.extend(super().generate_commands(**data))
        return commands


class TelnetModel:
    """
    Wrapper model aggregating independent Telnet configuration models for routers.
    """

    def __init__(self, session_manager):
        """
        Instantiates specific Telnet configuration models.
        """
        self.connection_section = TelnetConnectionModel(session_manager)
        self.login_section = TelnetLoginModel(session_manager)