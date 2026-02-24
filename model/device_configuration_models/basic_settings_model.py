from model.device_configuration_models.base_config_model import BaseConfigModel

class BasicSettingsModel(BaseConfigModel):
    def generate_commands(self, **kwargs) -> list[str]:
        commands = ["configure terminal"]

        if kwargs.get('encrypt_all'):
            commands.append("service password-encryption")

        if kwargs.get('hostname_enabled') and kwargs.get('hostname'):
            commands.append(f"hostname {kwargs.get('hostname')}")

        if kwargs.get('secret_enabled') and kwargs.get('secret'):
            commands.append(f"enable secret {kwargs.get('secret')}")

        if kwargs.get('banner_enabled') and kwargs.get('banner'):
            commands.append(f"banner motd ^{kwargs.get('banner')}^")

        if len(commands) <= 1:
            return []

        return commands