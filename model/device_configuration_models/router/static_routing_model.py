from model.device_configuration_models.base_interface_model import BaseInterfaceModel


class StaticRoutingModel(BaseInterfaceModel):
    """
    Model for generating Cisco IOS commands for static routing and fetching interfaces.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates static routing commands using network, mask, and next_hop parameters.
        """
        commands = []

        network = kwargs.get("network")
        mask = kwargs.get("mask")
        next_hop = kwargs.get("next_hop")

        if network and mask and next_hop:
            commands.append(f"ip route {network} {mask} {next_hop}")

        commands.extend(super().generate_commands(**kwargs))
        return commands