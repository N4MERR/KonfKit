class BaseConfigModel:

    def __init__(self, session_manager):
        self.session_manager = session_manager

    def generate_commands(self, **kwargs) -> list[str]:
        raise NotImplementedError

    def apply_configuration(self, **kwargs):
        commands = self.generate_commands(**kwargs)
        if commands:
            self.session_manager.send_command_set(commands)