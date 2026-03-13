from model.device_configuration_models.base_config_model import BaseConfigModel


class TelnetConnectionModel(BaseConfigModel):
    """
    Model for generating VTY line commands and management interface configuration for Telnet.
    """

    def generate_commands(self, **data) -> list[str]:
        """
        Generates commands for line range, transport, and management VLAN IP configuration.
        """
        commands = []
        write_memory = data.pop("_write_memory", False)

        if data.get("vty_enabled"):
            commands.append(f"line vty {data.get('vty_start')} {data.get('vty_end')}")
            commands.append("login local")
            commands.append("transport input telnet")
            commands.append("exit")

        vlan_id = data.get("vlan_id")
        ip_address = data.get("ip_address")
        subnet_mask = data.get("subnet_mask")
        default_gateway = data.get("default_gateway")

        if vlan_id and ip_address and subnet_mask:
            commands.append(f"interface vlan {vlan_id}")
            commands.append(f"ip address {ip_address} {subnet_mask}")
            commands.append("no shutdown")
            commands.append("exit")

        if default_gateway:
            commands.append(f"ip default-gateway {default_gateway}")

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
            commands.append(
                f"username {data.get('login_name')} privilege {privilege} secret {data.get('login_password')}")
            commands.append("exit")

        if write_memory:
            commands.append("do write memory")

        return commands


class TelnetModel:
    """
    Wrapper model aggregating independent Telnet configuration models for switches.
    """

    def __init__(self, session_manager):
        """
        Instantiates specific Telnet configuration models for switches.
        """
        self.connection_section = TelnetConnectionModel(session_manager)
        self.login_section = TelnetLoginModel(session_manager)