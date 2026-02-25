from model.device_configuration_models.base_config_model import BaseConfigModel

class SSHModel(BaseConfigModel):
    """
    Model for generating Cisco IOS commands for SSH configuration.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates Cisco CLI commands for SSH, domain name, and RSA keys based on enabled fields.
        """
        commands = ["configure terminal"]

        if kwargs.get('domain_enabled') and kwargs.get('domain'):
            commands.append(f"ip domain-name {kwargs.get('domain')}")

        if kwargs.get('key_size_enabled') and kwargs.get('key_size'):
            commands.append("crypto key generate rsa focus")
            commands.append(f"{kwargs.get('key_size')}")

        if kwargs.get('version_enabled') and kwargs.get('version'):
            commands.append(f"ip ssh version {kwargs.get('version')}")

        if kwargs.get('timeout_enabled') and kwargs.get('timeout'):
            commands.append(f"ip ssh time-out {kwargs.get('timeout')}")

        if kwargs.get('auth_retries_enabled') and kwargs.get('auth_retries'):
            commands.append(f"ip ssh authentication-retries {kwargs.get('auth_retries')}")

        return commands if len(commands) > 1 else []