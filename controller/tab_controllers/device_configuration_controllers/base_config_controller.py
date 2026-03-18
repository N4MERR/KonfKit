from PySide6.QtCore import QThread, Signal
from view.device_configuration_views.preview_dialog import PreviewDialog
from view.progress_dialog import ProgressDialog


class ConfigApplyWorker(QThread):
    """
    Native PySide worker class to handle applying configurations asynchronously.
    """
    finished_signal = Signal(bool, str)

    def __init__(self, session_manager, commands):
        super().__init__()
        self.session_manager = session_manager
        self.commands = commands

    def run(self):
        try:
            output = self.session_manager.send_command_set(self.commands)
            self.finished_signal.emit(True, output)
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class InterfaceLoadWorker(QThread):
    """
    Universal native PySide worker class to handle interface loading asynchronously.
    """
    finished_signal = Signal(list, str)

    def __init__(self, model):
        super().__init__()
        self.model = model

    def run(self):
        try:
            interfaces = self.model.get_interfaces()
            self.finished_signal.emit(interfaces if interfaces is not None else [], "")
        except Exception as e:
            self.finished_signal.emit([], str(e))


class BaseConfigController:
    """
    Base controller providing standard validation, preview, apply functionality,
    and dynamic interface loading for device configurations.
    """

    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.progress = None
        self.worker = None
        self.interface_worker = None

        if hasattr(self.view, 'preview_config_signal'):
            self.view.preview_config_signal.connect(self.handle_preview)
        if hasattr(self.view, 'apply_config_signal'):
            self.view.apply_config_signal.connect(self.handle_apply)

        # Universal dynamic binding for interface loading
        if hasattr(self.view, 'load_interfaces_signal') and hasattr(self.model, 'get_interfaces'):
            self.view.load_interfaces_signal.connect(self.handle_load_interfaces)

    def handle_load_interfaces(self, checked=False):
        """
        Universally handles querying device interfaces if the paired view and model support it.
        """
        self._show_progress("Loading interfaces from device...")

        self.interface_worker = InterfaceLoadWorker(self.model)

        def on_finished(interfaces, error_message):
            self._close_progress()

            if error_message:
                self._show_error(f"Failed to load interfaces: {error_message}")
            elif interfaces and hasattr(self.view, 'update_interfaces'):
                self.view.update_interfaces(interfaces)

            self.interface_worker.deleteLater()
            self.interface_worker = None

        self.interface_worker.finished_signal.connect(on_finished)
        self.interface_worker.start()

    def handle_preview(self, data=None):
        if data is None or not isinstance(data, dict):
            if not self.view.validate_all():
                return
            data = self.view.get_data()

        commands = self.model.generate_commands(**data)
        if commands:
            preview = PreviewDialog("\n".join(commands), self.view)
            preview.exec()
        else:
            self._show_error("No commands generated. Check configuration logic.")

    def handle_apply(self, data=None):
        if data is None or not isinstance(data, dict):
            if not self.view.validate_all():
                return
            data = self.view.get_data()

        commands = self.model.generate_commands(**data)

        if not commands:
            self._show_error("No configuration commands generated.")
            return

        self._show_progress("Applying configuration...")
        self.worker = ConfigApplyWorker(self.model.session_manager, commands)

        def on_finished(success, message):
            self._close_progress()

            if not success:
                self._show_error(f"Configuration failed: {message}")

            self.worker.deleteLater()
            self.worker = None

        self.worker.finished_signal.connect(on_finished)
        self.worker.start()

    def _show_progress(self, message):
        main_window = self.view.window()
        if main_window:
            self.progress = ProgressDialog(message, main_window)
            self.progress.show()

    def _close_progress(self):
        if self.progress:
            self.progress.close()
            self.progress = None

    def _show_error(self, message):
        main_window = self.view.window()
        if hasattr(main_window, 'show_error'):
            main_window.show_error(message)
        else:
            print(f"Error: {message}")