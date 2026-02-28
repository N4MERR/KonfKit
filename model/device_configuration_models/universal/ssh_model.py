from model.device_configuration_models.base_config_model import BaseConfigModel


class SSHGlobalModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for global SSH parameters.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates commands for domain name, RSA keys, SSH version, timeout, and retries.
        """
        commands = ["configure terminal"]

        if kwargs.get('domain_name_enabled') and kwargs.get('domain_name'):
            commands.append(f"ip domain-name {kwargs.get('domain_name')}")

        if kwargs.get('key_size_enabled') and kwargs.get('key_size'):
            commands.append(f"crypto key generate rsa modulus {kwargs.get('key_size')}")

        if kwargs.get('ssh_version_enabled') and kwargs.get('ssh_version'):
            commands.append(f"ip ssh version {kwargs.get('ssh_version')}")

        if kwargs.get('timeout_enabled') and kwargs.get('timeout'):
            commands.append(f"ip ssh time-out {kwargs.get('timeout')}")

        if kwargs.get('retries_enabled') and kwargs.get('retries'):
            commands.append(f"ip ssh authentication-retries {kwargs.get('retries')}")

        return commands if len(commands) > 1 else []


class SSHAuthModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for local SSH authentication.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates commands for creating a local username and secret password.
        """
        commands = ["configure terminal"]
        if kwargs.get('login_name') and kwargs.get('login_password'):
            commands.append(f"username {kwargs.get('login_name')} secret {kwargs.get('login_password')}")
        return commands if len(commands) > 1 else []


class SSHVtyModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for VTY line access.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates commands for VTY range, local login, and SSH transport.
        """
        commands = ["configure terminal"]
        if kwargs.get('vty_enabled'):
            commands.append(f"line vty {kwargs.get('vty_start')} {kwargs.get('vty_end')}")
            commands.append("login local")
            commands.append("transport input ssh")
            commands.append("exit")
        return commands if len(commands) > 1 else []