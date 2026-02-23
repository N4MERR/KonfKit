from model.device_configuration_models.base_config_model import BaseConfigModel


class OSPFBasicModel(BaseConfigModel):
    """
    Model for applying OSPF basic network configurations.
    """

    def apply_configuration(self, process_id: str, network: str, wildcard_mask: str, area: str, **kwargs):
        """
        Generates and sends basic OSPF network configuration commands.
        """
        commands = [
            "configure terminal",
            f"router ospf {process_id}",
            f"network {network} {wildcard_mask} area {area}"
        ]
        self.session_manager.send_command_set(commands)


class OSPFRouterIdModel(BaseConfigModel):
    """
    Model for applying OSPF Router ID configurations.
    """

    def apply_configuration(self, process_id: str, router_id: str, **kwargs):
        """
        Generates and sends OSPF router ID configuration commands.
        """
        commands = [
            "configure terminal",
            f"router ospf {process_id}",
            f"router-id {router_id}"
        ]
        self.session_manager.send_command_set(commands)


class OSPFPassiveInterfaceModel(BaseConfigModel):
    """
    Model for applying OSPF passive interface configurations.
    """

    def apply_configuration(self, process_id: str, interface_name: str, **kwargs):
        """
        Generates and sends OSPF passive interface configuration commands.
        """
        commands = [
            "configure terminal",
            f"router ospf {process_id}",
            f"passive-interface {interface_name}"
        ]
        self.session_manager.send_command_set(commands)


class OSPFDefaultRouteModel(BaseConfigModel):
    """
    Model for applying OSPF default route configurations.
    """

    def apply_configuration(self, process_id: str, always: bool = False, **kwargs):
        """
        Generates and sends OSPF default route advertisement commands.
        """
        always_flag = " always" if always else ""
        commands = [
            "configure terminal",
            f"router ospf {process_id}",
            f"default-information originate{always_flag}"
        ]
        self.session_manager.send_command_set(commands)