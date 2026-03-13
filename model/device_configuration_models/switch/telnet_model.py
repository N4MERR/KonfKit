from model.device_configuration_models.base_config_model import BaseConfigModel
from model.device_configuration_models.router.router_interface_model import BaseRouterInterfaceModel


class TelnetConnectionModel(BaseRouterInterfaceModel):
    """
    Model for generating VTY line commands and management interface configuration for Telnet.
    Inherits from BaseRouterInterfaceModel to cleanly reuse device interface querying logic.
    """

    def generate_commands(self, **data) -> list[str]:
        """
        Generates commands for line range, transport, management VLAN IP, and physical port assignment.
        """
        commands = []
        write_memory = data.pop("_write_memory", False)

        vty_enabled = data.get("vty_enabled", False)
        if vty_enabled:
            vty_start = str(data.get('vty_start', '')).strip()
            vty_end = str(data.get('vty_end', '')).strip()
            commands.append(f"line vty {vty_start} {vty_end}")
            commands.append("login local")
            commands.append("transport input telnet")
            commands.append("exit")

        vlan_id = str(data.get("vlan_id", "")).strip()
        ip_address = str(data.get("ip_address", "")).strip()
        subnet_mask = str(data.get("subnet_mask", "")).strip()
        default_gateway = str(data.get("default_gateway", "")).strip()
        management_interface = str(data.get("management_interface", "")).strip()

        if vlan_id and ip_address and subnet_mask:
            commands.append(f"interface vlan {vlan_id}")
            commands.append(f"ip address {ip_address} {subnet_mask}")
            commands.append("no shutdown")
            commands.append("exit")

            if management_interface:
                commands.append(f"interface {management_interface}")
                commands.append("switchport mode access")
                commands.append(f"switchport access vlan {vlan_id}")
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

        login_name = str(data.get("login_name", "")).strip()
        login_password = str(data.get("login_password", "")).strip()

        if login_name and login_password:
            privilege = str(data.get("privilege", "15")).strip()
            commands.append(f"username {login_name} privilege {privilege} secret {login_password}")
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