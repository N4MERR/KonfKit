from model.device_configuration_models.base_config_model import BaseConfigModel


class OSPFAreaModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for OSPF network advertisements.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates OSPF network commands using process_id, network, wildcard, and area keys.
        """
        commands = []

        process_id = kwargs.get("process_id")
        network = kwargs.get("network")
        wildcard = kwargs.get("wildcard_mask")
        area = kwargs.get("area")

        if process_id and network and wildcard and area is not None:
            commands.append(f"router ospf {process_id}")
            commands.append(f"network {network} {wildcard} area {area}")

        commands.extend(super().generate_commands(**kwargs))
        return commands


class OSPFRouterIdModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for OSPF Router ID.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates OSPF router-id command.
        """
        commands = []

        process_id = kwargs.get("process_id")
        router_id = kwargs.get("router_id")

        if process_id and router_id:
            commands.append(f"router ospf {process_id}")
            commands.append(f"router-id {router_id}")

        commands.extend(super().generate_commands(**kwargs))
        return commands


class OSPFPassiveInterfaceModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for OSPF passive interfaces.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates OSPF passive-interface command.
        """
        commands = []

        process_id = kwargs.get("process_id")
        interface = kwargs.get("interface_name")

        if process_id and interface:
            commands.append(f"router ospf {process_id}")
            commands.append(f"passive-interface {interface}")

        commands.extend(super().generate_commands(**kwargs))
        return commands


class OSPFModel:
    """
    Wrapper model aggregating physical and subinterface configuration logic.
    """

    def __init__(self, session_manager):
        """
        Initializes specific interface configuration models.
        """
        self.passive_interface_model = OSPFPassiveInterfaceModel(session_manager)
        self.router_id_model = OSPFRouterIdModel(session_manager)
        self.area_model = OSPFAreaModel(session_manager)