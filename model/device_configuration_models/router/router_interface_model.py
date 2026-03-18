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

        if data.get("ip_enabled") and data.get("ip_address") and data.get("subnet_mask"):
            commands.append(f"ip address {data.get('ip_address')} {data.get('subnet_mask')}")

        if data.get("ipv6_enabled") and data.get("ipv6_address") and data.get("ipv6_prefix"):
            prefix = data.get("ipv6_prefix").lstrip("/")
            commands.append(f"ipv6 address {data.get('ipv6_address')}/{prefix}")

        if data.get("enable_interface") is not None:
            if data.get("enable_interface"):
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

        if not data.get("interface") or not data.get("subinterface_id"):
            return commands

        target_iface = f"{data.get('interface')}.{data.get('subinterface_id')}"
        commands.append(f"interface {target_iface}")

        if data.get("vlan_id"):
            commands.append(f"encapsulation dot1Q {data.get('vlan_id')}")

        if data.get("ip_enabled") and data.get("ip_address") and data.get("subnet_mask"):
            commands.append(f"ip address {data.get('ip_address')} {data.get('subnet_mask')}")

        if data.get("ipv6_enabled") and data.get("ipv6_address") and data.get("ipv6_prefix"):
            prefix = data.get("ipv6_prefix").lstrip("/")
            commands.append(f"ipv6 address {data.get('ipv6_address')}/{prefix}")

        if data.get("enable_interface") is not None:
            if data.get("enable_interface"):
                commands.append("no shutdown")
            else:
                commands.append("shutdown")

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