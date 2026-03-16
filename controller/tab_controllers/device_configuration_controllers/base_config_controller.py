from PySide6.QtCore import QThread, Signal
from view.device_configuration_views.preview_dialog import PreviewDialog
from view.progress_dialog import ProgressDialog


class ConfigApplyWorker(QThread):
    """
    Native PySide worker class to handle applying configurations asynchronously.
    """
    finished_signal = Signal(bool, str)

    def __init__(self, session_manager, commands):
        """
        Initializes the worker with session management and the generated commands.
        """
        super().__init__()
        self.session_manager = session_manager
        self.commands = commands

    def run(self):
        """
        Executes the blocking configuration sending logic outside the UI event loop.
        Captures the exact error message instead of a generic fallback.
        """
        try:
            output = self.session_manager.send_command_set(self.commands)
            self.finished_signal.emit(True, output)
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class BaseConfigController:
    """
    Base controller providing standard validation, preview, and apply functionality for device configurations.
    """

    def __init__(self, view, model):
        """
        Connects standard view signals to controller actions.
        """
        self.view = view
        self.model = model
        self.progress = None
        self.worker = None

        if hasattr(self.view, 'preview_config_signal'):
            self.view.preview_config_signal.connect(self.handle_preview)
        if hasattr(self.view, 'apply_config_signal'):
            self.view.apply_config_signal.connect(self.handle_apply)

    def handle_preview(self, data=None):
        """
        Generates and displays the configuration commands without sending them to the device.
        """
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
        """
        Validates, generates, and asynchronously sends the configuration to the connected device.
        """
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
            """
            Handles the outcome of the configuration task and cleans up the worker.
            """
            self._close_progress()

            if not success:
                self._show_error(f"Configuration failed: {message}")

            self.worker.deleteLater()
            self.worker = None

        self.worker.finished_signal.connect(on_finished)
        self.worker.start()

    def _show_progress(self, message):
        """
        Helper to display a non-blocking progress dialog.
        """
        main_window = self.view.window()
        if main_window:
            self.progress = ProgressDialog(message, main_window)
            self.progress.show()

    def _close_progress(self):
        """
        Helper to safely close and remove the active progress dialog.
        """
        if self.progress:
            self.progress.close()
            self.progress = None

    def _show_error(self, message):
        """
        Helper to invoke the parent window's generic error display method.
        """
        main_window = self.view.window()
        if hasattr(main_window, 'show_error'):
            main_window.show_error(message)
        else:
            print(f"Error: {message}")