from PySide6.QtWidgets import QMessageBox, QApplication
from PySide6.QtCore import QThread, Signal

from controller.tab_controllers.device_configuration_controllers.router_interface_controller import \
    RouterInterfaceController

from view.progress_dialog import ProgressDialog
from model.network_session_manager import NetworkSessionManager
from model.terminal_model import TerminalModel
from model.device_configuration_models.router.ospf_model import OSPFModel
from model.device_configuration_models.router.dhcp_model import DHCPModel
from model.device_configuration_models.switch.vlan_model import VLANModel
from model.device_configuration_models.universal.system_settings_model import SystemSettingsModel
from model.device_configuration_models.router.telnet_model import TelnetModel as RouterTelnetModel
from model.device_configuration_models.switch.telnet_model import TelnetModel as SwitchTelnetModel
from model.device_configuration_models.universal.ssh_model import SSHModel
from model.device_configuration_models.router.router_interface_model import RouterInterfaceModel

from controller.tab_controllers.terminal_controller import TerminalController
from controller.tab_controllers.connection_profile_controller import ConnectionProfileController
from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController
from controller.tab_controllers.password_reset_controller import PasswordResetController


class ConnectionWorker(QThread):
    """
    Native PySide worker class to handle device connections asynchronously.
    """
    finished_signal = Signal(bool, str)

    def __init__(self, session_manager, settings):
        """
        Initializes the connection worker with session management and device settings.
        """
        super().__init__()
        self.session_manager = session_manager
        self.settings = settings

    def run(self):
        """
        Executes the blocking connection logic entirely outside the UI event loop.
        """
        success, message = self.session_manager.connect_device(self.settings)
        self.finished_signal.emit(success, message)


class InterfaceLoadWorker(QThread):
    """
    Native PySide worker class to handle interface loading asynchronously.
    """
    finished_signal = Signal(list, str)

    def __init__(self, model):
        """
        Initializes the interface worker with the designated model for querying device interfaces.
        """
        super().__init__()
        self.model = model

    def run(self):
        """
        Executes the blocking network query for interfaces outside the UI event loop.
        """
        try:
            interfaces = self.model.get_interfaces()
            self.finished_signal.emit(interfaces if interfaces is not None else [], "")
        except Exception as e:
            self.finished_signal.emit([], str(e))


class MainController:
    """
    Main application controller that coordinates between models and views while managing sub-controllers.
    """

    def __init__(self, window, profile_model):
        """
        Initializes the session manager and all sub-controllers for different device configurations.
        """
        self.window = window
        self.profile_model = profile_model
        self.session_manager = NetworkSessionManager()
        self.current_connection_data = None
        self.progress = None
        self.worker = None
        self.interface_worker = None

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

        self.password_reset_controller = PasswordResetController(
            self.window.password_reset_tab,
            self.session_manager,
            self.window.show_error
        )

        self.basic_settings_model = SystemSettingsModel(self.session_manager)

        self.router_basic_settings_controller = BaseConfigController(
            self.window.device_config_tab.router_basic_settings,
            self.basic_settings_model
        )
        self.switch_basic_settings_controller = BaseConfigController(
            self.window.device_config_tab.switch_basic_settings,
            self.basic_settings_model
        )

        self.router_telnet_model = RouterTelnetModel(self.session_manager)
        self.switch_telnet_model = SwitchTelnetModel(self.session_manager)

        self.router_telnet_connection_controller = BaseConfigController(
            self.window.device_config_tab.router_telnet_view.connection_section,
            self.router_telnet_model.connection_section
        )
        self.router_telnet_login_controller = BaseConfigController(
            self.window.device_config_tab.router_telnet_view.login_section,
            self.router_telnet_model.login_section
        )

        self.switch_telnet_connection_controller = BaseConfigController(
            self.window.device_config_tab.switch_telnet_view.connection_section,
            self.switch_telnet_model.connection_section
        )
        self.switch_telnet_login_controller = BaseConfigController(
            self.window.device_config_tab.switch_telnet_view.authentication_section,
            self.switch_telnet_model.authentication_section
        )

        self.ssh_model = SSHModel(self.session_manager)

        self.router_ssh_global_controller = BaseConfigController(
            self.window.device_config_tab.router_ssh_view.global_section,
            self.ssh_model.global_section
        )
        self.router_ssh_auth_controller = BaseConfigController(
            self.window.device_config_tab.router_ssh_view.auth_section,
            self.ssh_model.auth_section
        )

        self.switch_ssh_global_controller = BaseConfigController(
            self.window.device_config_tab.switch_ssh_view.global_section,
            self.ssh_model.global_section
        )
        self.switch_ssh_auth_controller = BaseConfigController(
            self.window.device_config_tab.switch_ssh_view.auth_section,
            self.ssh_model.auth_section
        )

        self.router_interface_model = RouterInterfaceModel(self.session_manager)

        self.router_physical_interface_controller = RouterInterfaceController(
            self.window.device_config_tab.router_interface_view.physical,
            self.router_interface_model.physical
        )
        self.router_subinterface_controller = RouterInterfaceController(
            self.window.device_config_tab.router_interface_view.subinterface,
            self.router_interface_model.subinterface
        )

        self.ospf_model = OSPFModel(self.session_manager)

        self.ospf_basic_controller = BaseConfigController(
            self.window.device_config_tab.ospf_view.basic_config,
            self.ospf_model.area_model
        )

        self.ospf_router_id_controller = BaseConfigController(
            self.window.device_config_tab.ospf_view.router_id,
            self.ospf_model.router_id_model
        )

        self.ospf_passive_int_controller = BaseConfigController(
            self.window.device_config_tab.ospf_view.passive_interfaces,
            self.ospf_model.passive_interface_model
        )

        self.dhcp_model = DHCPModel(self.session_manager)

        self.dhcp_pool_controller = BaseConfigController(
            self.window.device_config_tab.dhcp_view.pool_view,
            self.dhcp_model.dhcp_pool
        )
        self.dhcp_excluded_controller = BaseConfigController(
            self.window.device_config_tab.dhcp_view.excluded_view,
            self.dhcp_model.dhcp_excluded
        )

        self.vlan_model = VLANModel(self.session_manager)
        self.vlan_controller = BaseConfigController(
            self.window.device_config_tab.vlan_view,
            self.vlan_model
        )

        self._setup_connections()

    def _setup_connections(self):
        """
        Binds UI actions from the window and session manager signals to controller logic.
        """
        self.window.device_config_tab.close_tab_signal.connect(self.handle_session_close)
        self.window.device_config_tab.reconnect_signal.connect(self.handle_reconnect)
        self.session_manager.error_occurred.connect(self.window.show_error)
        self.session_manager.connection_lost.connect(self.handle_connection_lost)

        self.window.device_config_tab.switch_telnet_view.connection_section.load_interfaces_signal.connect(
            self.handle_load_switch_telnet_interfaces
        )

    def handle_load_switch_telnet_interfaces(self):
        """
        Fetches physical interfaces from the switch via a background worker and populates the management interface dropdown.
        """
        if not self.current_connection_data:
            self.window.show_error("No active connection to load interfaces.")
            return

        self.progress = ProgressDialog("Loading interfaces...", self.window)
        self.progress.show()

        self.interface_worker = InterfaceLoadWorker(self.switch_telnet_model.connection_section)

        def on_finished(interfaces, error_message):
            """
            Handles the completion of the background query and updates the UI state.
            """
            if self.progress:
                self.progress.close()
                self.progress = None

            if error_message:
                self.window.show_error(f"Failed to load interfaces: {error_message}")
            elif interfaces:
                self.window.device_config_tab.switch_telnet_view.connection_section.update_interfaces(interfaces)

            self.interface_worker.deleteLater()
            self.interface_worker = None

        self.interface_worker.finished_signal.connect(on_finished)
        self.interface_worker.start()

    def handle_session_close(self):
        """
        Safely terminates the active network session and returns to the home view.
        """
        self.current_connection_data = None
        self.session_manager.close_connection()
        self.window.show_home()

    def _start_async_connection(self, settings, message, is_reconnect=False, connection_data=None):
        """
        Internal method to spawn a QThread worker and safely show an active progress dialog.
        """
        self.progress = ProgressDialog(message, self.window)
        self.progress.show()

        QApplication.processEvents()

        self.worker = ConnectionWorker(self.session_manager, settings)

        def on_finished(success, error_message):
            """
            Handles the completion of the connection task and updates UI state.
            """
            if self.progress:
                self.progress.close()
                self.progress = None

            if success:
                if connection_data and not is_reconnect:
                    self.window.show_device_config(connection_data)
                    self.terminal_controller.reset_view()
                self.window.device_config_tab.set_connection_status(True)
                self.terminal_model.start_reading()
            else:
                self.window.device_config_tab.set_connection_status(False)
                prefix = "Reconnection failed" if is_reconnect else "Connection failed"
                self.window.show_error(f"{prefix} : {error_message}")
                if not is_reconnect:
                    self.window.show_home()

            self.worker.deleteLater()
            self.worker = None

        self.worker.finished_signal.connect(on_finished)
        self.worker.start()

    def handle_reconnect(self):
        """
        Attempts to reconnect via a non-blocking background thread.
        """
        if self.current_connection_data:
            self.session_manager.close_connection()
            netmiko_settings = {k: v for k, v in self.current_connection_data.items() if k != "name"}
            self._start_async_connection(netmiko_settings, "Reconnecting...", is_reconnect=True)

    def handle_connection_lost(self, message):
        """
        Updates the UI to reflect a disconnected state and prompts the user to reconnect.
        """
        self.window.device_config_tab.set_connection_status(False)

        reply = QMessageBox.question(
            self.window,
            "Connection Lost",
            f"The connection was unexpectedly closed.\nReason: {message}\n\nDo you want to reconnect?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.handle_reconnect()

    def handle_session_start(self, connection_data):
        """
        Initiates a device connection without freezing the UI.
        """
        self.current_connection_data = connection_data
        netmiko_settings = {k: v for k, v in connection_data.items() if k != "name"}
        name = connection_data.get('name', 'Device')
        self._start_async_connection(netmiko_settings, f"Connecting to {name}...", is_reconnect=False,
                                     connection_data=connection_data)