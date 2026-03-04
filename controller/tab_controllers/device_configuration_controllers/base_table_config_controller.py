from view.progress_dialog import ProgressDialog

class BaseTableConfigController:
    """
    Standardized controller for managing table-based row-by-row configurations.
    """

    def __init__(self, view, model):
        """
        Initializes the controller and binds the table view signals to logic.
        """
        self.view = view
        self.model = model
        self.progress_dialog = None
        self._setup_connections()

    def _setup_connections(self):
        """
        Connects standard load and session signals. Subclasses should call super()._setup_connections().
        """
        if hasattr(self.view, 'load_config_signal'):
            self.view.load_config_signal.connect(self.handle_load)

        self.model.session_manager.batch_finished.connect(self._close_progress)
        self.model.session_manager.error_occurred.connect(self._handle_error)

    def handle_load(self):
        """
        Triggers the model to fetch current configuration and populates the connected view.
        """
        self._show_progress("Loading configuration...")
        try:
            parsed_data = self.model.fetch_and_parse_config()
            self.view.populate_data(parsed_data)
        except Exception as e:
            print(f"Error loading config: {e}")
        finally:
            self._close_progress()

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
        Responds to session manager errors by closing progress.
        """
        self._close_progress()