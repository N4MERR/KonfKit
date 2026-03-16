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

        login_method = str(data.get('login_method', 'no login')).strip()

        if login_method == "login local":
            login_username = str(data.get("login_username", "")).strip()
            login_password = str(data.get("login_password", "")).strip()
            if login_username and login_password:
                login_privilege = str(data.get("login_privilege", "")).strip()
                if login_privilege:
                    commands.append(f"username {login_username} privilege {login_privilege} secret {login_password}")
                else:
                    commands.append(f"username {login_username} secret {login_password}")

        vty_enabled = data.get("vty_enabled", False)
        if vty_enabled:
            vty_start = str(data.get('vty_start', '')).strip()
            vty_end = str(data.get('vty_end', '')).strip()
            line_password = str(data.get('line_password', '')).strip()

            commands.append(f"line vty {vty_start} {vty_end}")

            if login_method == "login":
                if line_password:
                    commands.append(f"password {line_password}")
                commands.append("login")
            elif login_method == "no login":
                commands.append("no login")
            else:
                commands.append("login local")

            commands.append("transport input telnet")
            commands.append("exit")

        vlan_id = str(data.get("vlan_id", "")).strip()
        ip_address = str(data.get("ip_address", "")).strip()
        subnet_mask = str(data.get("subnet_mask", "")).strip()
        default_gateway = str(data.get("default_gateway", "")).strip()
        management_interface = str(data.get("management_interface", "")).strip()

        if vlan_id:
            if ip_address and subnet_mask:
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

        commands.extend(super().generate_commands(**data))
        return commands


class TelnetAuthenticationModel(BaseConfigModel):
    """
    Model for generating Telnet local user authentication commands.
    """

    def generate_commands(self, **data) -> list[str]:
        """
        Generates commands for username, optional privilege, password, and local login enforcement.
        """
        commands = []

        login_username = str(data.get("login_username", "")).strip()
        login_password = str(data.get("login_password", "")).strip()

        if login_username and login_password:
            privilege = str(data.get("privilege", "")).strip()
            if privilege:
                commands.append(f"username {login_username} privilege {privilege} secret {login_password}")
            else:
                commands.append(f"username {login_username} secret {login_password}")
            commands.append("exit")

        commands.extend(super().generate_commands(**data))
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
        self.authentication_section = TelnetAuthenticationModel(session_manager)