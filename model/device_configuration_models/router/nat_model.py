from model.device_configuration_models.base_interface_model import BaseInterfaceModel
import re


class NATInterfaceRoleModel(BaseInterfaceModel):
    """
    Model for applying interface-level NAT assignments.
    """

    def get_interfaces(self) -> list[str]:
        """
        Queries the device for available interfaces.
        """
        output = self.session_manager.send_command("show ip interface brief")
        if not output:
            return []

        interfaces = []
        for line in output.splitlines()[1:]:
            parts = line.split()
            if parts:
                interfaces.append(parts[0])
        return interfaces

    def generate_commands(self, **data) -> list[str]:
        """
        Generates commands for applying inside/outside roles to an interface.
        """
        commands = []
        interface = data.get("interface")
        role = data.get("role")

        if interface and role:
            commands.append(f"interface {interface}")
            commands.append(f"ip nat {role}")
            commands.append("exit")

        commands.extend(super().generate_commands(**data))
        return commands


class NATPoolCreationModel(BaseInterfaceModel):
    """
    Model for defining and creating a new NAT pool.
    """

    def generate_commands(self, **data) -> list[str]:
        """
        Generates the command payload to establish a NAT pool.
        """
        commands = []
        pool_name = data.get("pool_name")
        start_ip = data.get("start_ip")
        end_ip = data.get("end_ip")
        netmask = data.get("netmask")

        if pool_name and start_ip and end_ip and netmask:
            commands.append(f"ip nat pool {pool_name} {start_ip} {end_ip} netmask {netmask}")

        commands.extend(super().generate_commands(**data))
        return commands


class NATTranslationRuleModel(BaseInterfaceModel):
    """
    Model for handling static and dynamic NAT translation rules.
    """

    def get_interfaces(self) -> list[str]:
        """
        Queries the device for available interfaces.
        """
        output = self.session_manager.send_command("show ip interface brief")
        if not output:
            return []

        interfaces = []
        for line in output.splitlines()[1:]:
            parts = line.split()
            if parts:
                interfaces.append(parts[0])
        return interfaces

    def get_acls(self) -> list[str]:
        """
        Queries the device for configured Access Control Lists and preserves original parsing order.
        """
        output = self.session_manager.send_command("show ip access-lists")
        if not output:
            return []

        acls = []
        for line in output.splitlines():
            match = re.match(r'^(?:Standard|Extended|IPv4|IP) (?:IP )?access list (\S+)', line, re.IGNORECASE)
            if match:
                acls.append(match.group(1))

        return list(dict.fromkeys(acls))

    def get_pools(self) -> list[str]:
        """
        Queries the device for existing NAT pools and preserves original parsing order.
        """
        output = self.session_manager.send_command("show ip nat statistics")
        if not output:
            return []

        pools = []
        for line in output.splitlines():
            if "pool" in line.lower():
                match = re.search(r'pool (\S+):', line)
                if match:
                    pools.append(match.group(1))

        return list(dict.fromkeys(pools))

    def generate_commands(self, **data) -> list[str]:
        """
        Generates Cisco IOS commands for executing specific NAT translations.
        """
        commands = []
        source_type = data.get("source_type")
        overload = " overload" if data.get("overload") else ""

        if source_type == "static":
            inside_ip = data.get("inside_ip")
            outside_ip = data.get("outside_ip")
            if inside_ip and outside_ip:
                commands.append(f"ip nat inside source static {inside_ip} {outside_ip}")

        elif source_type == "list":
            acl = data.get("acl")
            mapping_type = data.get("mapping_type")

            if acl:
                if mapping_type == "interface":
                    target_iface = data.get("target_interface")
                    if target_iface:
                        commands.append(f"ip nat inside source list {acl} interface {target_iface}{overload}")
                elif mapping_type == "pool":
                    pool = data.get("pool")
                    if pool:
                        commands.append(f"ip nat inside source list {acl} pool {pool}{overload}")

        commands.extend(super().generate_commands(**data))
        return commands


class NATModel:
    """
    Container class aggregating isolated NAT data generation models.
    """

    def __init__(self, session_manager):
        """
        Instantiates independent models for the underlying components.
        """
        self.interface_role = NATInterfaceRoleModel(session_manager)
        self.pool_creation = NATPoolCreationModel(session_manager)
        self.translation_rule = NATTranslationRuleModel(session_manager)