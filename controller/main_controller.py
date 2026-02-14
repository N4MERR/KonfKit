from PySide6.QtCore import QThreadPool
from view.progress_dialog import ProgressDialog
from model.worker import Worker
from controller.tab_controllers.password_reset_controller import PasswordResetController
from controller.tab_controllers.connection_profile_controller import ConnectionProfileController
from model.network_session_manager import NetworkSessionManager

class MainController:
    """
    Coordinates application state and manages the unified NetworkSessionManager across views.
    """

    def __init__(self, window, model):
        self.window = window
        self.model = model

        self.session_manager = NetworkSessionManager()

        self.password_reset_ctrl = PasswordResetController(
            self.window.password_reset_tab,
            self.session_manager,
            self.window.show_error
        )

        self.connection_ctrl = ConnectionProfileController(
            self.window.connection_manager_tab,
            self.model,
            self.handle_start_session
        )

        self.window.device_config_tab.close_tab_signal.connect(self.handle_disconnect)
        self.progress_window = None

    def handle_start_session(self, connection_data):
        """
        Launches the connection worker thread.
        """
        self.progress_window = ProgressDialog("Connecting to device...", self.window)
        worker = Worker(self._connect_device, connection_data)
        worker.signals.result.connect(lambda res: self._on_connect_finished(res, connection_data))
        worker.signals.error.connect(lambda err: self._on_connect_finished((False, str(err[1])), connection_data))
        QThreadPool.globalInstance().start(worker)
        self.progress_window.exec()

    def _connect_device(self, connection_data):
        """
        Passes cleaned configuration data directly to the session manager.
        """
        netmiko_settings = {k: v for k, v in connection_data.items() if k != "name"}
        return self.session_manager.connect_device(netmiko_settings)

    def _on_connect_finished(self, result, connection_data):
        """
        Transitions to configuration view upon successful connection.
        """
        if self.progress_window:
            self.progress_window.close()

        success, message = result
        if success:
            terminal = self.window.device_config_tab.create_new_terminal()
            self._setup_terminal_signals(terminal)
            self.window.show_device_config(connection_data)
        else:
            self.window.show_error(f"Connection Failed: {message}")

    def _setup_terminal_signals(self, terminal):
        """
        Connects the unified session manager to the UI terminal widget.
        """
        try:
            self.session_manager.data_received.disconnect()
            self.session_manager.connection_lost.disconnect()
        except (TypeError, RuntimeError):
            pass

        self.session_manager.data_received.connect(terminal.append_output)
        self.session_manager.connection_lost.connect(self.handle_connection_lost)
        terminal.key_pressed.connect(self.session_manager.send_raw)

        terminal.set_terminal_enabled(True)

    def handle_disconnect(self):
        """
        Terminates the active session and cleans up UI components.
        """
        self.session_manager.close_connection()
        try:
            self.session_manager.data_received.disconnect()
            self.session_manager.connection_lost.disconnect()
        except (TypeError, RuntimeError):
            pass

        self.window.device_config_tab.cleanup_terminal()
        self.window.show_home()

    def handle_connection_lost(self, message):
        """
        Handles unexpected session termination.
        """
        if self.window.device_config_tab.terminal_widget:
            self.window.device_config_tab.terminal_widget.set_terminal_enabled(False)
        self.window.show_error(f"Session Terminated: {message}")
        self.handle_disconnect()