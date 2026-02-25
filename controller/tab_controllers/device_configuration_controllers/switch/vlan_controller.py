from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController

class VLANController(BaseConfigController):
    """
    Controller for the VLAN configuration section.
    """

    def handle_apply(self, data: dict):
        """
        Sends the VLAN commands to the session manager.
        """
        self._show_progress("Applying VLAN Configuration...")
        self.model.apply_configuration(**data)

    def handle_preview(self, data: dict):
        """
        Displays a preview of the VLAN commands.
        """
        super().handle_preview(data)