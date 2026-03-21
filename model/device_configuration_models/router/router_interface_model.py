from model.device_configuration_models.base_interface_model import BaseInterfaceModel


class RouterPhysicalInterfaceModel(BaseInterfaceModel):
    """
    Model handling the command generation for dual-stack physical router interfaces.
    """

    def generate_commands(self, **data) -> list[str]:
        """
        Transforms input data into Cisco IOS commands including IPv6 support for physical interfaces.
        """
        commands = []

        if not data.get("interface"):
            return commands

        commands.append(f"interface {data.get('interface')}")

        ip_config = data.get("ip_config", {})

        if ip_config.get("ipv4") and ip_config.get("ipv4_mask"):
            commands.append(f"ip address {ip_config.get('ipv4')} {ip_config.get('ipv4_mask')}")

        if ip_config.get("ipv6") and ip_config.get("ipv6_prefix"):
            prefix = str(ip_config.get("ipv6_prefix")).lstrip("/")
            commands.append(f"ipv6 address {ip_config.get('ipv6')}/{prefix}")

        status = data.get("status")
        if status is not None:
            if status:
                commands.append("no shutdown")
            else:
                commands.append("shutdown")

        commands.append("exit")

        commands.extend(super().generate_commands(**data))
        return commands


class RouterSubinterfaceModel(BaseInterfaceModel):
    """
    Model handling the command generation for dot1Q dual-stack subinterfaces.
    """

    def generate_commands(self, **data) -> list[str]:
        """
        Transforms input data into Cisco IOS commands for configuring dot1Q subinterfaces with IPv6 support.
        """
        commands = []

        if data.get("interface") is None or data.get("subinterface") is None:
            return commands

        target_iface = f"{data.get('interface')}.{data.get('subinterface')}"
        commands.append(f"interface {target_iface}")

        if data.get("vlan"):
            commands.append(f"encapsulation dot1Q {data.get('vlan')}")

        ip_config = data.get("ip_config", {})

        if ip_config.get("ipv4") and ip_config.get("ipv4_mask"):
            commands.append(f"ip address {ip_config.get('ipv4')} {ip_config.get('ipv4_mask')}")

        if ip_config.get("ipv6") and ip_config.get("ipv6_prefix"):
            prefix = str(ip_config.get("ipv6_prefix")).lstrip("/")
            commands.append(f"ipv6 address {ip_config.get('ipv6')}/{prefix}")

        commands.append("exit")

        commands.extend(super().generate_commands(**data))
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