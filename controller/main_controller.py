from PySide6.QtWidgets import QMessageBox, QApplication
from PySide6.QtCore import QThread, Signal

from controller.tab_controllers.device_configuration_controllers.router_interface_controller import \
    RouterInterfaceController
from view.progress_dialog import ProgressDialog
from model.network_session_manager import NetworkSessionManager
from model.terminal_model import TerminalModel
from model.device_configuration_models.router.ospf_model import (OSPFBasicModel, OSPFRouterIdModel,
                                                                 OSPFPassiveInterfaceModel, OSPFDefaultRouteModel)
from model.device_configuration_models.router.dhcp_model import DHCPModel
from model.device_configuration_models.switch.vlan_model import VLANModel
from model.device_configuration_models.universal.basic_settings_model import BasicSettingsModel
from model.device_configuration_models.universal.telnet_model import TelnetModel
from model.device_configuration_models.universal.ssh_model import SSHModel
from model.device_configuration_models.router.router_interface_model import RouterInterfaceModel

from controller.tab_controllers.terminal_controller import TerminalController
from controller.tab_controllers.connection_profile_controller import ConnectionProfileController
from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController


class ConnectionWorker(QThread):
    """
    Native PySide worker class to handle device connections asynchronously.
    """
    finished_signal = Signal(bool, str)

    def __init__(self, session_manager, settings):
        """
        Initializes the connection worker.
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


class MainController:
    """
    Main application controller that initializes the session manager and sub-controllers.
    """

    def __init__(self, window, profile_model):
        """
        Initializes the main controller with window and profile models.
        """
        self.window = window
        self.profile_model = profile_model
        self.session_manager = NetworkSessionManager()
        self.current_connection_data = None
        self.progress = None
        self.worker = None

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

        self.basic_settings_model = BasicSettingsModel(self.session_manager)

        self.router_basic_settings_controller = BaseConfigController(
            self.window.device_config_tab.router_basic_settings,
            self.basic_settings_model
        )
        self.switch_basic_settings_controller = BaseConfigController(
            self.window.device_config_tab.switch_basic_settings,
            self.basic_settings_model
        )

        self.telnet_model = TelnetModel(self.session_manager)

        self.router_telnet_connection_controller = BaseConfigController(
            self.window.device_config_tab.router_telnet_view.connection_section,
            self.telnet_model.connection_section
        )
        self.router_telnet_login_controller = BaseConfigController(
            self.window.device_config_tab.router_telnet_view.login_section,
            self.telnet_model.login_section
        )

        self.switch_telnet_connection_controller = BaseConfigController(
            self.window.device_config_tab.switch_telnet_view.connection_section,
            self.telnet_model.connection_section
        )
        self.switch_telnet_login_controller = BaseConfigController(
            self.window.device_config_tab.switch_telnet_view.login_section,
            self.telnet_model.login_section
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

        self.ospf_basic_model = OSPFBasicModel(self.session_manager)
        self.ospf_basic_controller = BaseConfigController(
            self.window.device_config_tab.ospf_view.basic_config,
            self.ospf_basic_model
        )

        self.ospf_router_id_model = OSPFRouterIdModel(self.session_manager)
        self.ospf_router_id_controller = BaseConfigController(
            self.window.device_config_tab.ospf_view.router_id,
            self.ospf_router_id_model
        )

        self.ospf_passive_int_model = OSPFPassiveInterfaceModel(self.session_manager)
        self.ospf_passive_int_controller = BaseConfigController(
            self.window.device_config_tab.ospf_view.passive_interfaces,
            self.ospf_passive_int_model
        )

        self.ospf_default_route_model = OSPFDefaultRouteModel(self.session_manager)
        self.ospf_default_route_controller = BaseConfigController(
            self.window.device_config_tab.ospf_view.default_route,
            self.ospf_default_route_model
        )

        self.dhcp_model = DHCPModel(self.session_manager)
        self.dhcp_controller = BaseConfigController(
            self.window.device_config_tab.dhcp_view,
            self.dhcp_model
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