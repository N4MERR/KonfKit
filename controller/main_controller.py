from PySide6.QtCore import QThreadPool
from view.progress_dialog import ProgressDialog
from model.worker import Worker
from controller.tab_controllers.password_reset_controller import PasswordResetController
from controller.tab_controllers.connection_controller import ConnectionController
from model.connection_managers.serial_connection_manager import SerialConnectionManager
from model.connection_managers.ssh_connection_manager import SSHConnectionManager
from model.connection_managers.telnet_connection_manager import TelnetConnectionManager


class MainController:
    """
    Coordinates application state and ensures active connection managers persist across view changes.
    """

    def __init__(self, window, model):
        self.window = window
        self.model = model

        self.serial_manager = SerialConnectionManager()
        self.ssh_manager = SSHConnectionManager()
        self.telnet_manager = TelnetConnectionManager()

        self.password_reset_ctrl = PasswordResetController(
            self.window.password_reset_tab,
            self.serial_manager,
            self.window.show_error
        )

        self.connection_ctrl = ConnectionController(
            self.window.connection_manager_tab,
            self.model,
            self.handle_start_session
        )

        self.window.device_config_tab.close_tab_signal.connect(self.handle_disconnect)
        self.active_manager = None
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
        Connects using the appropriate manager based on selected protocol.
        """
        protocol = connection_data.get("protocol", "SSH")
        host = connection_data.get("host")

        try:
            if protocol == "SSH":
                user = connection_data.get("username", "")
                pw = connection_data.get("password", "")
                port = int(connection_data.get("port", 22))
                return self.ssh_manager.connect_ssh(host, user, pw, port=port)

            elif protocol == "Telnet":
                port = int(connection_data.get("port", 23))
                return self.telnet_manager.connect_telnet(host, port=port)

            elif protocol == "Serial":
                return self.serial_manager.connect_serial(host, baudrate=int(connection_data.get("baud", 9600)))

            return False, "Unsupported protocol."
        except Exception as e:
            return False, str(e)

    def _on_connect_finished(self, result, connection_data):
        """
        Transitions to configuration view upon successful connection.
        """
        if self.progress_window:
            self.progress_window.close()

        success, message = result
        if success:
            self._setup_terminal_signals(connection_data.get("protocol"))
            self.window.show_device_config(connection_data)
        else:
            self.window.show_error(f"Connection Failed: {message}")

    def _setup_terminal_signals(self, protocol):
        """
        Maps hardware/socket signals to the UI terminal.
        """
        terminal = self.window.device_config_tab.terminal_widget

        if protocol == "SSH":
            self.active_manager = self.ssh_manager
        elif protocol == "Telnet":
            self.active_manager = self.telnet_manager
        elif protocol == "Serial":
            self.active_manager = self.serial_manager
        else:
            return

        try:
            self.active_manager.data_received.disconnect()
            self.active_manager.connection_lost.disconnect()
            terminal.key_pressed.disconnect()
        except (TypeError, RuntimeError):
            pass

        self.active_manager.data_received.connect(terminal.append_output)
        self.active_manager.connection_lost.connect(self.handle_connection_lost)
        terminal.key_pressed.connect(self.active_manager.send_input)

        terminal.set_terminal_enabled(True)

    def handle_disconnect(self):
        """
        Terminates the active session and cleans up UI when closing the configuration tab.
        """
        if self.active_manager:
            self.active_manager.close_connection()
            self.active_manager = None

        self.window.device_config_tab.terminal_widget.clear()
        self.window.device_config_tab.terminal_widget.set_terminal_enabled(False)
        self.window.show_home()

    def handle_connection_lost(self, message):
        """
        Handles unexpected socket closure.
        """
        self.window.device_config_tab.terminal_widget.set_terminal_enabled(False)
        self.window.show_error(f"Session Terminated: {message}")
        self.handle_disconnect()