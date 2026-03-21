from model.device_configuration_models.base_config_model import BaseConfigModel


class ACLModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for Access Control List configuration.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates standard, extended, or named ACL commands.
        """
        commands = []
        acl_type = kwargs.get("acl_type")
        acl_id = kwargs.get("acl_id", "")
        action = kwargs.get("action")
        protocol = kwargs.get("protocol")

        source_type = kwargs.get("source_type")
        source_ip = kwargs.get("source_ip")
        source_wildcard = kwargs.get("source_wildcard")

        destination_type = kwargs.get("destination_type")
        destination_ip = kwargs.get("destination_ip")
        destination_wildcard = kwargs.get("destination_wildcard")

        port_operator = kwargs.get("port_operator")
        port_number = kwargs.get("port_number")

        source_str = self._build_address_string(source_type, source_ip, source_wildcard)

        if "extended" in acl_type:
            dest_str = self._build_address_string(destination_type, destination_ip, destination_wildcard)
            port_str = ""
            if port_operator and port_operator != "none" and port_number:
                op = port_operator.split(" ")[0]
                port_str = f" {op} {port_number}"

            rule_str = f"{action} {protocol} {source_str} {dest_str}{port_str}"
        else:
            rule_str = f"{action} {source_str}"

        if "named" in acl_type:
            if "standard" in acl_type:
                commands.append(f"ip access-list standard {acl_id}")
            else:
                commands.append(f"ip access-list extended {acl_id}")
            commands.append(f" {rule_str}")
            commands.append(" exit")
        else:
            commands.append(f"access-list {acl_id} {rule_str}")

        commands.extend(super().generate_commands(**kwargs))
        return commands

    def _build_address_string(self, addr_type: str, ip: str, wildcard: str) -> str:
        """
        Formats the host/IP logic for Cisco ACL formatting.
        """
        if addr_type == "any":
            return "any"
        if addr_type == "host":
            return f"host {ip}"
        if addr_type == "ip":
            return f"{ip} {wildcard}"
        return "any"