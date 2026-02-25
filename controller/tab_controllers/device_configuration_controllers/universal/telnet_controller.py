"""
Controllers for managing Telnet configuration subsections.
"""
from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController

class TelnetAuthController(BaseConfigController):
    """
    Controller handling the Telnet authentication section.
    """
    def handle_apply(self, data: dict):
        """
        Applies local authentication credentials.
        """
        commands = self.model.generate_commands(**data)
        if commands:
            self._show_progress("Applying Telnet Authentication...")
            self.model.session_manager.send_batch(commands)

class TelnetVtyController(BaseConfigController):
    """
    Controller handling the Telnet VTY line section.
    """
    def handle_apply(self, data: dict):
        """
        Applies VTY line access settings.
        """
        commands = self.model.generate_commands(**data)
        if commands:
            self._show_progress("Applying Telnet VTY settings...")
            self.model.session_manager.send_batch(commands)