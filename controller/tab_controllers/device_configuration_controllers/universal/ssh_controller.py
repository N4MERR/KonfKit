from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController

class SSHGlobalController(BaseConfigController):
    """
    Controller handling global SSH settings section.
    """
    def handle_apply(self, data: dict):
        """
        Applies global SSH configuration batches.
        """
        commands = self.model.generate_commands(**data)
        if commands:
            self._show_progress("Applying Global SSH settings...")
            self.model.session_manager.send_batch(commands)

class SSHAuthController(BaseConfigController):
    """
    Controller handling mandatory local authentication section.
    """
    def handle_apply(self, data: dict):
        """
        Applies local user credentials.
        """
        commands = self.model.generate_commands(**data)
        if commands:
            self._show_progress("Applying SSH Authentication...")
            self.model.session_manager.send_batch(commands)

class SSHVtyController(BaseConfigController):
    """
    Controller handling VTY line range section.
    """
    def handle_apply(self, data: dict):
        """
        Applies VTY line access settings.
        """
        commands = self.model.generate_commands(**data)
        if commands:
            self._show_progress("Applying VTY Line settings...")
            self.model.session_manager.send_batch(commands)