from model.device_configuration_models.base_interface_model import BaseInterfaceModel


class StaticRoutingModel(BaseInterfaceModel):
    """
    Model for generating Cisco IOS commands for static routing and fetching interfaces.
    Handles dual-stack syntax variations between IPv4 and IPv6 protocols.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates static routing commands routing configuration data, adapting to the IP version.
        """
        commands = []

        version = kwargs.get("version")
        network = kwargs.get("network")
        mask = kwargs.get("mask")
        next_hop = kwargs.get("next_hop")

        if network and mask and next_hop:
            if version == "ipv4":
                commands.append(f"ip route {network} {mask} {next_hop}")
            elif version == "ipv6":
                clean_mask = mask.lstrip('/')
                commands.append(f"ipv6 route {network}/{clean_mask} {next_hop}")

        commands.extend(super().generate_commands(**kwargs))
        return commands