from model.network_session_manager import NetworkSessionManager
from model.terminal_model import TerminalModel
from controller.tab_controllers.terminal_controller import TerminalController
from controller.tab_controllers.connection_profile_controller import ConnectionProfileController


class MainController:
    """
    Main application controller that initializes the session manager and sub-controllers.
    """

    def __init__(self, window, profile_model):
        self.window = window
        self.profile_model = profile_model
        self.session_manager = NetworkSessionManager()

        self.terminal_view = self.window.device_config_tab.create_new_terminal()
        self.terminal_model = TerminalModel(self.session_manager)
        self.terminal_controller = TerminalController(
            self.terminal_model,
            self.terminal_view
        )

        self.profile_controller = ConnectionProfileController(
            self.window.connection_manager_tab,
            self.profile_model,
            self.handle_session_start
        )

        self._setup_connections()

    def _setup_connections(self):
        """
        Binds UI actions from the window to controller logic.
        """
        self.window.device_config_tab.close_tab_signal.connect(self.window.show_home)

    def handle_session_start(self, connection_data):
        """
        Initiates a connection and switches the UI to the device configuration tab.
        """
        self.window.show_device_config(connection_data)
        self.terminal_controller.reset_view()
        self.terminal_controller.log_info(f"Connecting to {connection_data.get('name', 'Device')}...")

        netmiko_settings = {k: v for k, v in connection_data.items() if k != "name"}

        success, message = self.session_manager.connect_device(netmiko_settings)
        if success:
            self.terminal_model.start_reading()
            self.terminal_controller.log_info("Connection established.")
        else:
            self.window.show_error(message)
            self.window.show_home()