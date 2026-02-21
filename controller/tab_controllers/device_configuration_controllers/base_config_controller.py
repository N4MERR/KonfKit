from view.progress_dialog import ProgressDialog

class BaseConfigController:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.progress_dialog = None
        self._setup_connections()

    def _setup_connections(self):
        self.view.apply_config_signal.connect(self.handle_apply)
        self.model.session_manager.batch_finished.connect(self._close_progress)
        self.model.session_manager.error_occurred.connect(self._handle_error)

    def handle_apply(self, data: dict):
        raise NotImplementedError

    def _show_progress(self, message="Processing..."):
        if not self.progress_dialog:
            self.progress_dialog = ProgressDialog(message, self.view)
        self.progress_dialog.show()

    def _close_progress(self):
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

    def _handle_error(self, message):
        self._close_progress()