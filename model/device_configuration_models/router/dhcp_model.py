from model.device_configuration_models.base_config_model import BaseConfigModel


class DHCPPoolModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for DHCP pool configuration.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates commands for creating and configuring a DHCP pool.
        """
        commands = []

        pool_name = kwargs.get("pool_name")
        network = kwargs.get("network")
        mask = kwargs.get("mask")
        gateway = kwargs.get("gateway")
        dns = kwargs.get("dns")
        domain = kwargs.get("domain_name")

        if pool_name:
            commands.append(f"ip dhcp pool {pool_name}")
            if network and mask:
                commands.append(f" network {network} {mask}")
            if gateway:
                commands.append(f" default-router {gateway}")
            if dns:
                commands.append(f" dns-server {dns}")
            if domain:
                commands.append(f" domain-name {domain}")
            commands.append(" exit")

        if kwargs.get("_write_memory"):
            commands.append("do write memory")

        return commands


class DHCPExcludedModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for excluded DHCP addresses.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates commands to exclude specific IP addresses from DHCP allocation.
        """
        commands = []

        start_ip = kwargs.get("start_ip")
        end_ip = kwargs.get("end_ip")

        if start_ip:
            if end_ip:
                commands.append(f"ip dhcp excluded-address {start_ip} {end_ip}")
            else:
                commands.append(f"ip dhcp excluded-address {start_ip}")

        if kwargs.get("_write_memory"):
            commands.append("do write memory")

        return commands


class DHCPModel:
    """
    Container model that holds sub-models for DHCP Pool and DHCP Excluded address configurations.
    """

    def __init__(self, session_manager):
        """
        Initializes the DHCP sub-models with the shared network session manager.
        """
        self.dhcp_pool = DHCPPoolModel(session_manager)
        self.dhcp_excluded = DHCPExcludedModel(session_manager)