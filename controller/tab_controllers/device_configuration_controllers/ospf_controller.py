from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController

class OSPFController(BaseConfigController):
    def handle_apply(self, data: dict):
        if all(data.values()):
            self._show_progress("Applying OSPF configuration...")
            self.model.apply_configuration(**data)
            self.view.clear_inputs()