from model.device_configuration_models.base_config_model import BaseConfigModel


class VLANModel(BaseConfigModel):
    """
    Model handling the logic for generating Cisco IOS commands for VLAN setup.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates Cisco CLI commands for creating VLANs and assigning optional names.
        """
        commands = []

        vlan_id = kwargs.get("vlan_id")
        if vlan_id:
            commands.append(f"vlan {vlan_id}")
            if kwargs.get("name_enabled") and kwargs.get("vlan_name"):
                commands.append(f"name {kwargs.get('vlan_name')}")
            commands.append("exit")

        commands.extend(super().generate_commands(**kwargs))
        return commands