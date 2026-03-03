from model.device_configuration_models.base_config_model import BaseConfigModel


class OSPFBasicModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for OSPF network advertisements.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates OSPF network commands using process_id, network, wildcard, and area keys.
        """
        commands = []
        write_memory = kwargs.pop("_write_memory", False)

        process_id = kwargs.get("process_id")
        network = kwargs.get("network")
        wildcard = kwargs.get("wildcard_mask")
        area = kwargs.get("area")

        if process_id and network and wildcard and area is not None:
            commands.append(f"router ospf {process_id}")
            commands.append(f"network {network} {wildcard} area {area}")

        if write_memory:
            commands.append("do write memory")

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
        write_memory = kwargs.pop("_write_memory", False)

        process_id = kwargs.get("process_id")
        router_id = kwargs.get("router_id")

        if process_id and router_id:
            commands.append(f"router ospf {process_id}")
            commands.append(f"router-id {router_id}")

        if write_memory:
            commands.append("do write memory")

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
        write_memory = kwargs.pop("_write_memory", False)

        process_id = kwargs.get("process_id")
        interface = kwargs.get("interface_name")

        if process_id and interface:
            commands.append(f"router ospf {process_id}")
            commands.append(f"passive-interface {interface}")

        if write_memory:
            commands.append("do write memory")

        return commands


class OSPFDefaultRouteModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for OSPF default route origination.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates OSPF default-information originate command.
        """
        commands = []
        write_memory = kwargs.pop("_write_memory", False)

        process_id = kwargs.get("process_id")
        always = kwargs.get("always", False)

        if process_id:
            command = "default-information originate"
            if always:
                command += " always"
            commands.append(f"router ospf {process_id}")
            commands.append(command)

        if write_memory:
            commands.append("do write memory")

        return commands