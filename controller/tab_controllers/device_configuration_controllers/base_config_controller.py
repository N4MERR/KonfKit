from view.device_configuration_views.preview_dialog import PreviewDialog
from view.progress_dialog import ProgressDialog


class BaseConfigController:
    """
    Standardized controller for managing Cisco device configurations with fixed signal handling.
    """

    def __init__(self, view, model):
        """
        Initializes the controller and binds standardized view signals to logic.
        """
        self.view = view
        self.model = model
        self.progress_dialog = None
        self._setup_connections()

    def _setup_connections(self):
        """
        Connects the unified apply and preview signals from the view layer.
        """
        if hasattr(self.view, 'apply_config_signal'):
            self.view.apply_config_signal.connect(self.handle_apply)
        if hasattr(self.view, 'preview_config_signal'):
            self.view.preview_config_signal.connect(self.handle_preview)

        self.model.session_manager.batch_finished.connect(self._close_progress)
        self.model.session_manager.error_occurred.connect(self._handle_error)

    def handle_apply(self, data: dict):
        """
        Processes the application of configuration data to the active device session and appends memory write if requested.
        """
        write_memory = data.pop("_write_memory", False)

        if hasattr(self.model, 'generate_config'):
            commands = self.model.generate_config(data)
        else:
            commands = self.model.generate_commands(**data)

        if not commands:
            return

        if write_memory:
            commands.append("do write memory")

        self._show_progress("Applying configuration...")
        self.model.session_manager.send_command_set(commands)

    def handle_preview(self, data: dict):
        """
        Generates commands from the model, appends memory write if requested, and displays them in a preview dialog.
        """
        write_memory = data.pop("_write_memory", False)

        if hasattr(self.model, 'generate_config'):
            commands = self.model.generate_config(data)
        else:
            commands = self.model.generate_commands(**data)

        if not commands:
            return

        if write_memory:
            commands.append("do write memory")

        preview_text = "\n".join(commands)
        dialog = PreviewDialog(preview_text, self.view)
        dialog.exec()

    def _show_progress(self, message="Processing..."):
        """
        Displays a modal progress dialog during device communication.
        """
        if not self.progress_dialog:
            self.progress_dialog = ProgressDialog(message, self.view)
        self.progress_dialog.show()

    def _close_progress(self):
        """
        Safely hides and removes the progress dialog.
        """
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

    def _handle_error(self, message):
        """
        Responds to session manager errors by closing progress and reporting feedback.
        """
        self._close_progress()