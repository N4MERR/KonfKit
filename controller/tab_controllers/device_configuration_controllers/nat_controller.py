from PySide6.QtCore import QThread, Signal
from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController
from controller.tab_controllers.device_configuration_controllers.load_workers import NatLoadWorker


class NATTranslationRuleController(BaseConfigController):
    """
    Controller coordinating data loading and command generation for the translation rules.
    """

    def __init__(self, view, model):
        """
        Connects dynamic logic for querying existing pools, ACLs, and interfaces.
        """
        super().__init__(view, model)
        self.worker = None

        self.view.load_acls_signal.connect(lambda: self._start_loading("acls"))
        self.view.load_pools_signal.connect(lambda: self._start_loading("pools"))

    def _start_loading(self, data_type: str):
        """
        Triggers the background thread for NAT-specific data.
        """
        self._show_progress(f"Loading {data_type} from device...")
        self.worker = NatLoadWorker(self.model, data_type)

        def on_finished(type_loaded, data):
            """
            Internal callback to handle UI updates and dialog closure.
            """
            self._close_progress()

            if type_loaded == "acls":
                self.view.update_acls(data)
            elif type_loaded == "pools":
                self.view.update_pools(data)

            if self.worker:
                self.worker.deleteLater()
                self.worker = None

        self.worker.finished_signal.connect(on_finished)
        self.worker.start()


class NATController:
    """
    Wrapper acting as the primary hook point for integrating NAT controllers into the tab.
    """

    def __init__(self, view, model):
        """
        Routes the sub-views and sub-models into their designated controllers.
        Uses BaseConfigController directly where no custom logic is required.
        """
        self.interface_role = BaseConfigController(view.interface_role, model.interface_role)
        self.pool_creation = BaseConfigController(view.pool_creation, model.pool_creation)
        self.translation_rule = NATTranslationRuleController(view.translation_rule, model.translation_rule)