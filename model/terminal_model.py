import threading
import time
from PySide6.QtCore import QObject, Signal

class TerminalModel(QObject):
    """
    Handles terminal data processing by subscribing to the session manager's data signals.
    """
    data_ready = Signal(str)
    connection_state_changed = Signal(bool)

    def __init__(self, session_manager):
        super().__init__()
        self.session_manager = session_manager
        self._running = False
        self.session_manager.data_received.connect(self._handle_incoming_data)
        self.session_manager.connection_lost.connect(self._handle_disconnection)

    def start_reading(self):
        """
        Activates the terminal state tracking.
        """
        if self._running:
            return
        self._running = True
        self.connection_state_changed.emit(True)

    def stop_reading(self):
        """
        Deactivates the terminal state tracking.
        """
        self._running = False
        self.connection_state_changed.emit(False)

    def _handle_incoming_data(self, data):
        """
        Proxies data from the session manager to the UI if the terminal is active.
        """
        if self._running:
            self.data_ready.emit(data)

    def _handle_disconnection(self, message):
        """
        Updates the internal state when the network session is terminated.
        """
        self.stop_reading()

    def send_input(self, text):
        """
        Transmits raw user input to the active network session.
        """
        if self.session_manager.connection:
            self.session_manager.send_raw(text)