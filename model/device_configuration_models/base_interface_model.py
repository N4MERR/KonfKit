import re
from model.device_configuration_models.base_config_model import BaseConfigModel


class BaseInterfaceModel(BaseConfigModel):
    """
    Base model providing the utility to fetch interface lists from any Cisco device
    while ignoring virtual interfaces like VLANs.
    """

    def get_interfaces(self) -> list[str]:
        """
        Queries the device for a list of IP interfaces, parses the output, and excludes VLANs.
        """
        output = self.session_manager.send_command("show ip interface brief")
        if not output:
            return []

        interfaces = []
        for line in output.split('\n'):
            match = re.match(r'^([A-Za-z]+\s*\d+(?:/\d+)*)\s+', line.strip())
            if match:
                iface = match.group(1).replace(" ", "")
                if not iface.lower().startswith("vlan"):
                    interfaces.append(iface)

        return interfaces