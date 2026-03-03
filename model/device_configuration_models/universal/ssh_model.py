from model.device_configuration_models.base_config_model import BaseConfigModel


class SSHModel(BaseConfigModel):
    """
    Model handling the logic for generating Cisco IOS commands for all SSH configuration sections.
    """

    def generate_commands(self, **data):
        """
        Transforms validated user input dictionaries into a list of Cisco configuration commands based on the section type.
        """
        commands = []
        write_memory = data.pop("_write_memory", False)
        config_type = data.get("type")

        if config_type == "ssh_global":
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

        elif config_type == "ssh_auth":
            if data.get("login_name") and data.get("login_password"):
                commands.append(f"username {data.get('login_name')} privilege 15 secret {data.get('login_password')}")

        elif config_type == "ssh_vty":
            if data.get("vty_enabled"):
                commands.append(f"line vty {data.get('vty_start')} {data.get('vty_end')}")
                commands.append("login local")
                commands.append("transport input ssh")
                commands.append("exit")

        if write_memory:
            commands.append("do write memory")

        return commands