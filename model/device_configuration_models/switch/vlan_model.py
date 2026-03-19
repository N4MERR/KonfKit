import re
from model.device_configuration_models.base_interface_model import BaseInterfaceModel
from model.device_configuration_models.base_config_model import BaseConfigModel


class CreateVlanModel(BaseConfigModel):
    """
    Model handling the logic for generating Cisco IOS commands to create a VLAN and its SVI.
    """

    def generate_commands(self, **data) -> list[str]:
        """
        Transforms VLAN creation parameters into Cisco IOS configuration commands.
        """
        commands = []

        vlan_id = data.get("vlan_id")
        vlan_name = data.get("vlan_name")
        vlan_ip = data.get("vlan_ip")
        vlan_mask = data.get("vlan_mask")

        if vlan_id:
            commands.append(f"vlan {vlan_id}")
            if vlan_name:
                commands.append(f"name {vlan_name}")
            commands.append("exit")

            if vlan_ip and vlan_mask:
                commands.append(f"interface vlan {vlan_id}")
                commands.append(f"ip address {vlan_ip} {vlan_mask}")
                commands.append("no shutdown")
                commands.append("exit")

        commands.extend(super().generate_commands(**data))
        return commands


class InterfaceVlanModel(BaseInterfaceModel):
    """
    Model handling the logic for generating Cisco IOS commands for VLAN access and trunk port configuration.
    """

    def get_vlans(self) -> list[str]:
        """
        Queries the device for existing VLANs, parses the output, and returns a list of active VLAN IDs.
        """
        output = self.session_manager.send_command("show vlan brief")
        if not output:
            return []

        vlans = []
        for line in output.split('\n'):
            match = re.match(r'^(\d+)\s+', line.strip())
            if match:
                vlans.append(match.group(1))

        return vlans

    def generate_commands(self, **data) -> list[str]:
        """
        Transforms selected interface and VLAN parameters into Cisco IOS configuration commands based on mode.
        """
        commands = []

        interface = data.get("interface")
        mode = data.get("mode")

        if interface and mode:
            commands.append(f"interface {interface}")
            commands.append(f"switchport mode {mode}")

            if mode == "access":
                access_vlan = data.get("access_vlan")
                if access_vlan:
                    commands.append(f"switchport access vlan {access_vlan}")
            elif mode == "trunk":
                trunk_vlans = data.get("trunk_vlans", [])
                native_vlan = data.get("native_vlan")

                if trunk_vlans:
                    vlan_string = ",".join(trunk_vlans)
                    commands.append(f"switchport trunk allowed vlan {vlan_string}")

                if native_vlan:
                    commands.append(f"switchport trunk native vlan {native_vlan}")

            commands.append("exit")

        commands.extend(super().generate_commands(**data))
        return commands


class VlanModel:
    """
    Wrapper model aggregating VLAN creation and interface assignment logic.
    """

    def __init__(self, session_manager):
        """
        Initializes specific VLAN configuration models.
        """
        self.create_vlan_model = CreateVlanModel(session_manager)
        self.interface_vlan_model = InterfaceVlanModel(session_manager)