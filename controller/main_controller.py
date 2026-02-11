from PySide6.QtCore import QThreadPool
from view.progress_dialog import ProgressDialog
from model.worker import Worker
from controller.tabs.password_reset_controller import PasswordResetController
from controller.tabs.connection_controller import ConnectionController
from model.serial_connection_manager import SerialConnectionManager
from model.ssh_connection_manager import SSHConnectionManager
from model.telnet_connection_manager import TelnetConnectionManager


class MainController:
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

        self.window.device_config_tab.home_requested.connect(self.window.show_home)
        self.progress_window = None

    def handle_start_session(self, connection_data):
        self.progress_window = ProgressDialog("Connecting to device...", self.window)

        worker = Worker(self._connect_device, connection_data)
        worker.signals.result.connect(lambda res: self._on_connect_finished(res, connection_data))
        worker.signals.error.connect(lambda err: self._on_connect_finished((False, str(err[1])), connection_data))

        QThreadPool.globalInstance().start(worker)
        self.progress_window.exec()

    def _connect_device(self, connection_data):
        protocol = connection_data.get("protocol", "SSH")
        host = connection_data.get("host")
        user = connection_data.get("username")
        pw = connection_data.get("password")

        try:
            if protocol == "SSH":
                self.ssh_manager.connect_ssh(host, user, pw)
            elif protocol == "Telnet":
                self.telnet_manager.connect_telnet(host)
            elif protocol == "Serial":
                self.serial_manager.port = host
                self.serial_manager.open_serial_connection()
            return True, "Success"
        except Exception as e:
            return False, str(e)

    def _on_connect_finished(self, result, connection_data):
        if self.progress_window:
            self.progress_window.close()
            self.progress_window = None

        success, message = result
        if success:
            self.window.show_device_config(connection_data)
        else:
            self.window.show_error(f"Failed to connect:\n{message}")