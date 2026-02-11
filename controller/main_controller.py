from controller.tabs.password_reset_controller import PasswordResetController
from controller.tabs.connection_controller import ConnectionController
from model.serial_connection_manager import SerialConnectionManager
from model.ssh_connection_manager import SSHConnectionManager
from model.telnet_connection_manager import TelnetConnectionManager

class MainController:
    """
    Top-level controller initializing protocol-specific managers and routing sessions.
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

    def handle_start_session(self, connection_data):
        protocol = connection_data.get("protocol", "SSH")
        host = connection_data.get("host")
        user = connection_data.get("username")
        pw = connection_data.get("password")

        if protocol == "SSH":
            self.ssh_manager.connect_ssh(host, user, pw)
        elif protocol == "Telnet":
            self.telnet_manager.connect_telnet(host)
        elif protocol == "Serial":
            self.serial_manager.port = host
            self.serial_manager.open_serial_connection()