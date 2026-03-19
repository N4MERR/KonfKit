from PySide6.QtWidgets import QMessageBox, QApplication
from PySide6.QtCore import QThread, Signal

from view.progress_dialog import ProgressDialog
from model.network_session_manager import NetworkSessionManager
from model.terminal_model import TerminalModel
from model.device_configuration_models.router.ospf_model import OSPFModel
from model.device_configuration_models.router.dhcp_model import DHCPModel
from model.device_configuration_models.switch.vlan_model import VlanModel
from model.device_configuration_models.universal.system_settings_model import SystemSettingsModel
from model.device_configuration_models.router.telnet_model import TelnetModel as RouterTelnetModel
from model.device_configuration_models.switch.telnet_model import TelnetModel as SwitchTelnetModel
from model.device_configuration_models.router.ssh_model import SSHModel as RouterSSHModel
from model.device_configuration_models.switch.ssh_model import SSHModel as SwitchSSHModel
from model.device_configuration_models.router.router_interface_model import RouterInterfaceModel
from model.device_configuration_models.switch.etherchannel_model import EtherChannelModel

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
        Initializes the connection worker with the session manager and settings.
        """
        super().__init__()
        self.session_manager = session_manager
        self.settings = settings

    def run(self):
        """
        Executes the device connection process in a separate thread.
        """
        success, message = self.session_manager.connect_device(self.settings)
        self.finished_signal.emit(success, message)


class MainController:
    """
    Main application controller that coordinates between models and views while managing sub-controllers.
    """

    def __init__(self, window, profile_model):
        """
        Initializes the primary controller, establishing links between models, views, and sub-controllers.
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

        self.router_ssh_model = RouterSSHModel(self.session_manager)
        self.switch_ssh_model = SwitchSSHModel(self.session_manager)

        self.router_ssh_global_controller = BaseConfigController(
            self.window.device_config_tab.router_ssh_view.global_section,
            self.router_ssh_model.global_section
        )
        self.router_ssh_auth_controller = BaseConfigController(
            self.window.device_config_tab.router_ssh_view.auth_section,
            self.router_ssh_model.auth_section
        )

        self.switch_ssh_global_controller = BaseConfigController(
            self.window.device_config_tab.switch_ssh_view.global_section,
            self.switch_ssh_model.global_section
        )
        self.switch_ssh_auth_controller = BaseConfigController(
            self.window.device_config_tab.switch_ssh_view.auth_section,
            self.switch_ssh_model.auth_section
        )

        self.router_interface_model = RouterInterfaceModel(self.session_manager)

        self.router_physical_interface_controller = BaseConfigController(
            self.window.device_config_tab.router_interface_view.physical,
            self.router_interface_model.physical
        )
        self.router_subinterface_controller = BaseConfigController(
            self.window.device_config_tab.router_interface_view.subinterface,
            self.router_interface_model.subinterface
        )

        self.etherchannel_model = EtherChannelModel(self.session_manager)
        self.etherchannel_controller = BaseConfigController(
            self.window.device_config_tab.switch_etherchannel_view,
            self.etherchannel_model
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

        self.vlan_model = VlanModel(self.session_manager)

        self.create_vlan_controller = BaseConfigController(
            self.window.device_config_tab.vlan_view.create_vlan,
            self.vlan_model.create_vlan_model
        )

        self.interface_vlan_controller = BaseConfigController(
            self.window.device_config_tab.vlan_view.interface_vlan,
            self.vlan_model.interface_vlan_model
        )

        self._setup_connections()

    def _setup_connections(self):
        """
        Binds primary UI signals to their corresponding controller slot methods.
        """
        self.window.device_config_tab.close_tab_signal.connect(self.handle_session_close)
        self.window.device_config_tab.reconnect_signal.connect(self.handle_reconnect)
        self.session_manager.error_occurred.connect(self.window.show_error)
        self.session_manager.connection_lost.connect(self.handle_connection_lost)

    def handle_session_close(self):
        """
        Clears connection data, shuts down active sessions, and returns to the home view.
        """
        self.current_connection_data = None
        self.session_manager.close_connection()
        self.window.show_home()

    def _start_async_connection(self, settings, message, is_reconnect=False, connection_data=None):
        """
        Initializes an asynchronous connection attempt with user feedback via a progress dialog.
        """
        self.progress = ProgressDialog(message, self.window)
        self.progress.show()
        QApplication.processEvents()

        self.worker = ConnectionWorker(self.session_manager, settings)

        def on_finished(success, error_message):
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
        Attempts to restart the existing session parameters if a valid connection state exists.
        """
        if self.current_connection_data:
            self.session_manager.close_connection()
            netmiko_settings = {k: v for k, v in self.current_connection_data.items() if k != "name"}
            self._start_async_connection(netmiko_settings, "Reconnecting...", is_reconnect=True)

    def handle_connection_lost(self, message):
        """
        Alerts the user of an unexpected disconnect and provides an option to immediately reconnect.
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
        Initiates a new device session from connection profile data.
        """
        self.current_connection_data = connection_data
        netmiko_settings = {k: v for k, v in connection_data.items() if k != "name"}
        name = connection_data.get('name', 'Device')
        self._start_async_connection(netmiko_settings, f"Connecting to {name}...", is_reconnect=False,
                                     connection_data=connection_data)