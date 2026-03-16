class BaseConfigModel:
    """
    Base model class handling configuration generation for network devices.
    """

    def __init__(self, session_manager):
        """
        Initializes the configuration model with a network session manager.
        """
        self.session_manager = session_manager

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates base configuration commands like saving configuration.
        """
        commands = []
        if kwargs.get("_save_configuration", False):
            commands.extend(["end", "copy running-config startup-config"])
        return commands