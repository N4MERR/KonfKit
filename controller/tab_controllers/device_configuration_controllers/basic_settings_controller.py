from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController

class BasicSettingsController(BaseConfigController):
    """
    Controller handling application and preview of basic device settings.
    """

    def handle_apply(self, data: dict):
        """
        Requests the model to apply the configuration using data validated by the view.
        """
        self._show_progress("Applying basic settings...")
        self.model.apply_configuration(**data)

    def handle_preview(self, data: dict):
        """
        Triggers the configuration preview dialog for basic settings.
        """
        super().handle_preview(data)