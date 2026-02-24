from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController

class BasicSettingsController(BaseConfigController):
    """
    Controller for managing the basic settings configuration flow.
    """

    def handle_apply(self, data: dict):
        """
        Triggers the model to apply basic settings to the device and shows progress.
        """
        self._show_progress("Applying basic settings...")
        self.model.apply_configuration(**data)