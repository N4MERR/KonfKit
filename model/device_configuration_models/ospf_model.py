from model.device_configuration_models.base_config_model import BaseConfigModel

class OSPFBasicModel(BaseConfigModel):
    """
    Model for applying OSPF basic network configurations.
    """

    def generate_commands(self, process_id: str, network: str, wildcard_mask: str, area: str, **kwargs) -> list[str]:
        """
        Generates basic OSPF network configuration commands.
        """
        return [
            "configure terminal",
            f"router ospf {process_id}",
            f"network {network} {wildcard_mask} area {area}"
        ]


class OSPFRouterIdModel(BaseConfigModel):
    """
    Model for applying OSPF Router ID configurations.
    """

    def generate_commands(self, process_id: str, router_id: str, **kwargs) -> list[str]:
        """
        Generates OSPF router ID configuration commands.
        """
        return [
            "configure terminal",
            f"router ospf {process_id}",
            f"router-id {router_id}"
        ]


class OSPFPassiveInterfaceModel(BaseConfigModel):
    """
    Model for applying OSPF passive interface configurations.
    """

    def generate_commands(self, process_id: str, interface_name: str, **kwargs) -> list[str]:
        """
        Generates OSPF passive interface configuration commands.
        """
        return [
            "configure terminal",
            f"router ospf {process_id}",
            f"passive-interface {interface_name}"
        ]


class OSPFDefaultRouteModel(BaseConfigModel):
    """
    Model for applying OSPF default route configurations.
    """

    def generate_commands(self, process_id: str, always: bool = False, **kwargs) -> list[str]:
        """
        Generates OSPF default route advertisement commands.
        """
        always_flag = " always" if always else ""
        return [
            "configure terminal",
            f"router ospf {process_id}",
            f"default-information originate{always_flag}"
        ]