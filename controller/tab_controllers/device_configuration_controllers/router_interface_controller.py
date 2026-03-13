from PySide6.QtCore import QThread, Signal
from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController


class RouterInterfaceLoadWorker(QThread):
    """
    Native PySide worker class to handle router interface loading asynchronously.
    """
    finished_signal = Signal(list)

    def __init__(self, model):
        """
        Initializes the worker with the specific model for interface retrieval.
        """
        super().__init__()
        self.model = model

    def run(self):
        """
        Executes the blocking interface query outside the UI event loop.
        """
        try:
            interfaces = self.model.get_interfaces()
            self.finished_signal.emit(interfaces if interfaces is not None else [])
        except Exception:
            self.finished_signal.emit([])


class RouterInterfaceController(BaseConfigController):
    """
    Specialized controller handling the dynamic fetching of interfaces alongside standard configuration processing.
    """

    def __init__(self, view, model):
        """
        Connects standard signals and binds the interface refresh action.
        """
        super().__init__(view, model)
        self.worker = None
        self.view.refresh_interfaces_signal.connect(self.handle_refresh)

    def handle_refresh(self):
        """
        Triggers a background worker to query interfaces from the device and securely updates the view.
        """
        self._show_progress("Loading interfaces from device...")

        self.worker = RouterInterfaceLoadWorker(self.model)

        def on_finished(interfaces):
            """
            Processes the retrieved interfaces and closes the progress dialog.
            """
            self._close_progress()

            if interfaces:
                self.view.update_interfaces(interfaces)

            self.worker.deleteLater()
            self.worker = None

        self.worker.finished_signal.connect(on_finished)
        self.worker.start()