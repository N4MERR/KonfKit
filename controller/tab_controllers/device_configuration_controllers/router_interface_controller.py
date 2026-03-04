from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController


class RouterInterfaceController(BaseConfigController):
    """
    Specialized controller handling the dynamic fetching of interfaces alongside standard configuration processing.
    """

    def __init__(self, view, model):
        """
        Connects standard signals and binds the interface refresh action.
        """
        super().__init__(view, model)
        self.view.refresh_interfaces_signal.connect(self.handle_refresh)

    def handle_refresh(self):
        """
        Triggers the model to query interfaces from the device and updates the view.
        """
        self._show_progress("Loading interfaces from device...")
        interfaces = self.model.get_interfaces()
        if interfaces is not None:
            self.view.update_interfaces(interfaces)
        self._close_progress()