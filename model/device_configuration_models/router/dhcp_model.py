import re
from model.device_configuration_models.base_config_model import BaseConfigModel

class DHCPModel(BaseConfigModel):
    """
    Handles parsing and specific row-level command generation for DHCP configurations.
    """

    def fetch_and_parse_config(self) -> dict:
        """
        Parses the running config to extract current DHCP status.
        """
        raw_output = self.session_manager.send_command("show running-config | section dhcp")
        parsed_data = {"excluded_addresses": [], "pools": {}}

        excl_regex = re.compile(r"ip dhcp excluded-address ([\d\.]+)(?:\s+([\d\.]+))?")
        pool_regex = re.compile(r"ip dhcp pool (\S+)")
        net_regex = re.compile(r"network ([\d\.]+ [\d\.]+)")
        gw_regex = re.compile(r"default-router ([\d\.]+)")

        current_pool = None
        for line in raw_output.splitlines():
            line = line.strip()

            excl_match = excl_regex.search(line)
            if excl_match:
                parsed_data["excluded_addresses"].append(excl_match.groups())
                continue

            pool_match = pool_regex.search(line)
            if pool_match:
                current_pool = pool_match.group(1)
                parsed_data["pools"][current_pool] = {"network": "", "default_router": ""}
                continue

            if current_pool:
                net_match = net_regex.search(line)
                if net_match:
                    parsed_data["pools"][current_pool]["network"] = net_match.group(1)

                gw_match = gw_regex.search(line)
                if gw_match:
                    parsed_data["pools"][current_pool]["default_router"] = gw_match.group(1)

        return parsed_data

    def generate_pool_commands(self, data: dict) -> list[str]:
        """
        Generates commands for a DHCP pool, including a 'no' command for clean overwrites.
        """
        commands = ["configure terminal"]
        name = data.get("name")
        commands.append(f"no ip dhcp pool {name}")
        commands.append(f"ip dhcp pool {name}")

        network = data.get("network")
        if network:
            commands.append(f" network {network}")

        default_router = data.get("default_router")
        if default_router:
            commands.append(f" default-router {default_router}")

        commands.append(" exit")
        commands.append("end")
        return commands

    def generate_delete_pool_commands(self, data: dict) -> list[str]:
        """
        Generates commands to remove a DHCP pool.
        """
        return ["configure terminal", f"no ip dhcp pool {data.get('name')}", "end"]

    def generate_exclusion_commands(self, data: dict) -> list[str]:
        """
        Generates commands for an excluded address range.
        """
        commands = ["configure terminal"]
        start = data.get("start")
        end = data.get("end")
        cmd = f"ip dhcp excluded-address {start}"
        if end:
            cmd += f" {end}"
        commands.append(cmd)
        commands.append("end")
        return commands

    def generate_delete_exclusion_commands(self, data: dict) -> list[str]:
        """
        Generates commands to remove an excluded address range.
        """
        commands = ["configure terminal"]
        start = data.get("start")
        end = data.get("end")
        cmd = f"no ip dhcp excluded-address {start}"
        if end:
            cmd += f" {end}"
        commands.append(cmd)
        commands.append("end")
        return commands