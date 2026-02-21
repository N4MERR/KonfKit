class BaseConfigModel:
    """
    Base model class providing common dependencies and batch execution logic for device configurations.
    """

    def __init__(self, session_manager):
        """
        Initializes the base configuration model with a session manager.
        """
        self.session_manager = session_manager

    def generate_commands(self, **kwargs) -> list[tuple]:
        """
        Must be implemented by child classes to generate specific protocol command lists.
        """
        raise NotImplementedError

    def apply_configuration(self, **kwargs):
        """
        Executes the generated configuration commands through the network session manager.
        """
        commands = self.generate_commands(**kwargs)
        if commands:
            self.session_manager.execute_batch(commands)