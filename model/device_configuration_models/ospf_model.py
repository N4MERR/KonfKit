from model.device_configuration_models.base_config_model import BaseConfigModel

class OSPFBasicModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for OSPF network advertisements.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates OSPF network commands using process_id, network, wildcard, and area keys.
        """
        process_id = kwargs.get("process_id")
        network = kwargs.get("network")
        wildcard = kwargs.get("wildcard_mask")
        area = kwargs.get("area")

        if not process_id or not network or not wildcard or area is None:
            return []

        return [
            "configure terminal",
            f"router ospf {process_id}",
            f"network {network} {wildcard} area {area}"
        ]

class OSPFRouterIdModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for OSPF Router ID.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates OSPF router-id command.
        """
        process_id = kwargs.get("process_id")
        router_id = kwargs.get("router_id")

        if not process_id or not router_id:
            return []

        return [
            "configure terminal",
            f"router ospf {process_id}",
            f"router-id {router_id}"
        ]

class OSPFPassiveInterfaceModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for OSPF passive interfaces.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates OSPF passive-interface command.
        """
        process_id = kwargs.get("process_id")
        interface = kwargs.get("interface_name")

        if not process_id or not interface:
            return []

        return [
            "configure terminal",
            f"router ospf {process_id}",
            f"passive-interface {interface}"
        ]

class OSPFDefaultRouteModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for OSPF default route origination.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates OSPF default-information originate command.
        """
        process_id = kwargs.get("process_id")
        always = kwargs.get("always", False)

        if not process_id:
            return []

        command = "default-information originate"
        if always:
            command += " always"

        return [
            "configure terminal",
            f"router ospf {process_id}",
            command
        ]