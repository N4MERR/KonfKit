from PySide6.QtCore import QObject

class TerminalController(QObject):
    """
    Coordinates data transfer between TerminalModel and TerminalView.
    """
    def __init__(self, model, view):
        super().__init__()
        self.model = model
        self.view = view
        self._setup_connections()

    def _setup_connections(self):
        """
        Links model signals to view slots and vice versa.
        """
        self.view.user_input_received.connect(self.model.send_input)
        self.model.data_ready.connect(self.view.display_text)
        self.model.connection_state_changed.connect(self.view.apply_style)

    def log_info(self, message):
        """
        Routes informational messages to the view.
        """
        self.view.display_system_message(message)

    def reset_view(self):
        """
        Instructs the view to clear its buffer.
        """
        self.view.clear_screen()