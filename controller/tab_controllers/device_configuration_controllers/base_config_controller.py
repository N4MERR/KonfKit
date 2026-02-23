from view.device_configuration_views.preview_dialog import PreviewDialog
from view.progress_dialog import ProgressDialog


class BaseConfigController:
    """
    Base controller class managing signals from device configuration views.
    """

    def __init__(self, view, model):
        """
        Initializes the controller with view and model, and sets up connections.
        """
        self.view = view
        self.model = model
        self.progress_dialog = None
        self._setup_connections()

    def _setup_connections(self):
        """
        Connects view signals and session manager signals to controller handlers.
        """
        self.view.apply_config_signal.connect(self.handle_apply)
        self.view.preview_config_signal.connect(self.handle_preview)
        self.model.session_manager.batch_finished.connect(self._close_progress)
        self.model.session_manager.error_occurred.connect(self._handle_error)

    def handle_apply(self, data: dict):
        """
        Must be implemented by child classes to handle applying configuration.
        """
        raise NotImplementedError

    def handle_preview(self, data: dict):
        """
        Generates configuration commands and displays them in a terminal-like preview dialog.
        """
        commands = self.model.generate_commands(**data)
        preview_text = "\n".join(commands)

        dialog = PreviewDialog(preview_text, self.view)
        if dialog.exec():
            self.handle_apply(data)

    def _show_progress(self, message="Processing..."):
        """
        Displays a progress dialog with the given message.
        """
        if not self.progress_dialog:
            self.progress_dialog = ProgressDialog(message, self.view)
        self.progress_dialog.show()

    def _close_progress(self):
        """
        Closes the progress dialog.
        """
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

    def _handle_error(self, message):
        """
        Handles errors reported by the session manager.
        """
        self._close_progress()