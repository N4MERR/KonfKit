import re
from model.device_configuration_models.base_interface_model import BaseInterfaceModel


class EtherChannelModel(BaseInterfaceModel):
    """
    Model handling the logic for generating Cisco IOS commands for EtherChannel grouping and automatic trunk provisioning.
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
        Transforms selected interfaces into a grouped range command, safely shuts them down, applies the channel mode and trunking, and brings them back up.
        """
        commands = []

        interfaces = data.get("etherchannel", [])
        channel_group = data.get("channel_group")
        channel_mode = data.get("channel_mode")

        if interfaces and channel_group and channel_mode:
            range_string = " , ".join(interfaces)

            commands.append(f"interface range {range_string}")
            commands.append("shutdown")
            commands.append(f"channel-group {channel_group} mode {channel_mode}")

            allowed_vlans = data.get("allowed_vlans", [])
            if allowed_vlans:
                commands.append("switchport mode trunk")
                vlan_string = ",".join(allowed_vlans)
                commands.append(f"switchport trunk allowed vlan {vlan_string}")

            commands.append("no shutdown")
            commands.append("exit")

        commands.extend(super().generate_commands(**data))
        return commands