from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController

class TelnetController(BaseConfigController):
    """
    Controller handling application and preview of Telnet configuration.
    """

    def handle_apply(self, data: dict):
        """
        Requests the model to apply Telnet settings using data validated by the view.
        """
        self._show_progress("Applying Telnet settings...")
        self.model.apply_configuration(**data)

    def handle_preview(self, data: dict):
        """
        Triggers the configuration preview dialog for Telnet.
        """
        super().handle_preview(data)