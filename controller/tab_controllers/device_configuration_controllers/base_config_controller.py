from PySide6.QtWidgets import QDialog
from view.device_configuration_views.preview_dialog import PreviewDialog
from view.progress_dialog import ProgressDialog
from .workers import ConfigApplyWorker, InterfaceLoadWorker, VlanLoadWorker


class BaseConfigController:
    """
    Base controller providing standard validation, preview, apply functionality,
    and dynamic data loading for device configurations.
    """

    def __init__(self, view, model):
        """
        Initializes the controller and binds all standard UI signals dynamically based on view capabilities.
        """
        self.view = view
        self.model = model
        self.progress = None
        self.worker = None
        self.interface_worker = None
        self.vlan_worker = None

        if hasattr(self.view, 'preview_config_signal'):
            self.view.preview_config_signal.connect(self.handle_preview)
        if hasattr(self.view, 'apply_config_signal'):
            self.view.apply_config_signal.connect(self.handle_apply)

        if hasattr(self.view, 'load_interfaces_signal') and hasattr(self.model, 'get_interfaces'):
            self.view.load_interfaces_signal.connect(self.handle_load_interfaces)

        if hasattr(self.view, 'load_vlans_signal') and hasattr(self.model, 'get_vlans'):
            self.view.load_vlans_signal.connect(self.handle_load_vlans)

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

    def handle_load_vlans(self, checked=False):
        """
        Universally handles querying device VLANs if the paired view and model support it.
        """
        self._show_progress("Loading VLANs from device...")

        self.vlan_worker = VlanLoadWorker(self.model)

        def on_finished(vlans, error_message):
            self._close_progress()

            if error_message:
                self._show_error(f"Failed to load VLANs: {error_message}")
            elif vlans and hasattr(self.view, 'update_vlans'):
                self.view.update_vlans(vlans)

            self.vlan_worker.deleteLater()
            self.vlan_worker = None

        self.vlan_worker.finished_signal.connect(on_finished)
        self.vlan_worker.start()

    def handle_preview(self, data=None):
        """
        Validates UI inputs and constructs a preview dialog for generated device commands.
        If the user accepts the dialog, the configuration is applied without re-validation.
        """
        if data is None or not isinstance(data, dict):
            if not self.view.validate_all():
                return
            data = self.view.get_data()

        commands = self.model.generate_commands(**data)
        if commands:
            preview = PreviewDialog("\n".join(commands), self.view)
            if preview.exec() == QDialog.Accepted:
                self._apply_direct(commands)
        else:
            self._show_error("No commands generated. Check configuration logic.")

    def handle_apply(self, data=None):
        """
        Validates UI inputs, generates commands, and immediately deploys them to the active session asynchronously.
        """
        if data is None or not isinstance(data, dict):
            if not self.view.validate_all():
                return
            data = self.view.get_data()

        commands = self.model.generate_commands(**data)

        if not commands:
            self._show_error("No configuration commands generated.")
            return

        self._apply_direct(commands)

    def _apply_direct(self, commands: list[str]):
        """
        Internal helper to deploy a set of commands without further validation or UI data retrieval.
        """
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
        """
        Constructs and displays a modal progress overlay.
        """
        main_window = self.view.window()
        if main_window:
            self.progress = ProgressDialog(message, main_window)
            self.progress.show()

    def _close_progress(self):
        """
        Terminates the active progress dialog safely.
        """
        if self.progress:
            self.progress.close()
            self.progress = None

    def _show_error(self, message):
        """
        Escalates error messages back to the main application window context.
        """
        main_window = self.view.window()
        if hasattr(main_window, 'show_error'):
            main_window.show_error(message)
        else:
            print(f"Error: {message}")