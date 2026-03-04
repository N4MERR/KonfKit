import re
from model.device_configuration_models.base_config_model import BaseConfigModel


class BaseRouterInterfaceModel(BaseConfigModel):
    """
    Base model providing the utility to fetch interface lists from a router.
    """

    def get_interfaces(self) -> list[str]:
        """
        Queries the device for a list of IP interfaces and parses the output.
        """
        output = self.session_manager.send_command("show ip interface brief")
        if not output:
            return []

        interfaces = []
        for line in output.split('\n'):
            match = re.match(r'^([A-Za-z]+\s*\d+(?:/\d+)*)\s+', line.strip())
            if match:
                iface = match.group(1).replace(" ", "")
                interfaces.append(iface)

        return interfaces


class RouterPhysicalInterfaceModel(BaseRouterInterfaceModel):
    """
    Model handling the command generation for physical router interfaces.
    """

    def generate_commands(self, **data) -> list[str]:
        """
        Transforms input data into Cisco IOS commands for configuring physical interfaces.
        """
        commands = []
        write_memory = data.pop("_write_memory", False)

        if not data.get("interface"):
            return commands

        commands.append(f"interface {data.get('interface')}")

        if data.get("ip_enabled") and data.get("ip_address") and data.get("subnet_mask"):
            commands.append(f"ip address {data.get('ip_address')} {data.get('subnet_mask')}")

        if data.get("enable_interface"):
            commands.append("no shutdown")
        else:
            commands.append("shutdown")

        commands.append("exit")

        if write_memory:
            commands.append("do write memory")

        return commands


class RouterSubinterfaceModel(BaseRouterInterfaceModel):
    """
    Model handling the command generation for dot1Q subinterfaces.
    """

    def generate_commands(self, **data) -> list[str]:
        """
        Transforms input data into Cisco IOS commands for configuring dot1Q subinterfaces.
        """
        commands = []
        write_memory = data.pop("_write_memory", False)

        if not data.get("interface") or not data.get("subinterface_id"):
            return commands

        target_iface = f"{data.get('interface')}.{data.get('subinterface_id')}"
        commands.append(f"interface {target_iface}")

        if data.get("vlan_id"):
            commands.append(f"encapsulation dot1Q {data.get('vlan_id')}")

        if data.get("ip_enabled") and data.get("ip_address") and data.get("subnet_mask"):
            commands.append(f"ip address {data.get('ip_address')} {data.get('subnet_mask')}")

        if data.get("enable_interface"):
            commands.append("no shutdown")
        else:
            commands.append("shutdown")

        commands.append("exit")

        if write_memory:
            commands.append("do write memory")

        return commands


class RouterInterfaceModel:
    """
    Wrapper model aggregating physical and subinterface configuration logic.
    """

    def __init__(self, session_manager):
        """
        Initializes specific interface configuration models.
        """
        self.physical = RouterPhysicalInterfaceModel(session_manager)
        self.subinterface = RouterSubinterfaceModel(session_manager)