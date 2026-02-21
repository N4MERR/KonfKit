from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController

class OSPFController(BaseConfigController):
    """
    Controller handling user interactions for the OSPF configuration tab.
    """

    def handle_apply(self, data: dict):
        """
        Applies configuration data to the model and updates the view upon successful application.
        """
        self._show_progress("Applying OSPF configuration...")
        self.model.apply_configuration(**data)
        self.view.clear_inputs()