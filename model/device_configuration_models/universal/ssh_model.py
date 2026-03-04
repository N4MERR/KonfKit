from model.device_configuration_models.base_config_model import BaseConfigModel


class SSHConnectionModel(BaseConfigModel):
    """
    Model handling the logic for generating Cisco IOS commands for the SSH connection section.
    """

    def generate_commands(self, **data):
        """
        Transforms validated user input into global SSH configuration commands.
        """
        commands = []
        write_memory = data.pop("_write_memory", False)

        if data.get("hostname"):
            commands.append(f"hostname {data.get('hostname')}")

        if data.get("domain_name"):
            commands.append(f"ip domain-name {data.get('domain_name')}")

        if data.get("rsa_modulus"):
            commands.append(f"crypto key generate rsa modulus {data.get('rsa_modulus')}")

        if data.get("ssh_version"):
            commands.append(f"ip ssh version {data.get('ssh_version')}")

        if data.get("ssh_timeout_enabled") and data.get("ssh_timeout"):
            commands.append(f"ip ssh time-out {data.get('ssh_timeout')}")

        if data.get("ssh_retries_enabled") and data.get("ssh_retries"):
            commands.append(f"ip ssh authentication-retries {data.get('ssh_retries')}")

        if data.get("vty_enabled"):
            commands.append(f"line vty {data.get('vty_start')} {data.get('vty_end')}")
            commands.append("transport input ssh")
            commands.append("exit")

        if write_memory:
            commands.append("do write memory")

        return commands


class SSHLoginModel(BaseConfigModel):
    """
    Model handling the logic for generating Cisco IOS commands for the SSH login authentication section.
    """

    def generate_commands(self, **data):
        """
        Transforms validated user input into SSH local authentication commands.
        """
        commands = []
        write_memory = data.pop("_write_memory", False)

        if data.get("login_name") and data.get("login_password"):
            privilege = data.get("privilege")
            commands.append(f"username {data.get('login_name')} privilege {privilege} secret {data.get('login_password')}")
            commands.append("exit")

        if write_memory:
            commands.append("do write memory")

        return commands


class SSHModel:
    """
    Wrapper model aggregating independent SSH configuration models.
    """

    def __init__(self, session_manager):
        """
        Instantiates specific SSH configuration models.
        """
        self.global_section = SSHConnectionModel(session_manager)
        self.auth_section = SSHLoginModel(session_manager)