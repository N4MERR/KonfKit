from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController

class OSPFBasicController(BaseConfigController):
    """
    Controller handling execution requests for OSPF network advertisements.
    """

    def handle_apply(self, data: dict):
        """
        Requests model to apply OSPF networks using data validated by the view.
        """
        self._show_progress("Applying OSPF networks...")
        self.model.apply_configuration(**data)

    def handle_preview(self, data: dict):
        """
        Displays the command preview window for OSPF networks.
        """
        super().handle_preview(data)


class OSPFRouterIdController(BaseConfigController):
    """
    Controller handling execution requests for OSPF Router ID.
    """

    def handle_apply(self, data: dict):
        """
        Requests model to apply OSPF Router ID using data validated by the view.
        """
        self._show_progress("Applying OSPF Router ID...")
        self.model.apply_configuration(**data)

    def handle_preview(self, data: dict):
        """
        Displays the command preview window for OSPF Router ID.
        """
        super().handle_preview(data)


class OSPFPassiveInterfaceController(BaseConfigController):
    """
    Controller handling execution requests for OSPF passive interfaces.
    """

    def handle_apply(self, data: dict):
        """
        Requests model to apply OSPF passive interfaces using data validated by the view.
        """
        self._show_progress("Applying OSPF passive interfaces...")
        self.model.apply_configuration(**data)

    def handle_preview(self, data: dict):
        """
        Displays the command preview window for OSPF passive interfaces.
        """
        super().handle_preview(data)


class OSPFDefaultRouteController(BaseConfigController):
    """
    Controller handling execution requests for OSPF default route advertisement.
    """

    def handle_apply(self, data: dict):
        """
        Requests model to apply OSPF default route using data validated by the view.
        """
        self._show_progress("Applying OSPF default route...")
        self.model.apply_configuration(**data)

    def handle_preview(self, data: dict):
        """
        Displays the command preview window for OSPF default route.
        """
        super().handle_preview(data)