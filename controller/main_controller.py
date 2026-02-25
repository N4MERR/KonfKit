"""
Main application controller that initializes the session manager and sub-controllers.
"""
from model.network_session_manager import NetworkSessionManager
from model.terminal_model import TerminalModel
from model.device_configuration_models.router.ospf_model import (OSPFBasicModel, OSPFRouterIdModel,
                                                                 OSPFPassiveInterfaceModel, OSPFDefaultRouteModel)
from model.device_configuration_models.universal.basic_settings_model import BasicSettingsModel
from model.device_configuration_models.universal.telnet_model import TelnetAuthModel, TelnetVtyModel
from model.device_configuration_models.universal.ssh_model import SSHGlobalModel, SSHAuthModel, SSHVtyModel

from controller.tab_controllers.terminal_controller import TerminalController
from controller.tab_controllers.connection_profile_controller import ConnectionProfileController
from controller.tab_controllers.device_configuration_controllers.router.ospf_controller import (
    OSPFBasicController, OSPFRouterIdController, OSPFPassiveInterfaceController, OSPFDefaultRouteController
)
from controller.tab_controllers.device_configuration_controllers.universal.basic_settings_controller import \
    BasicSettingsController
from controller.tab_controllers.device_configuration_controllers.universal.telnet_controller import (
    TelnetAuthController, TelnetVtyController
)
from controller.tab_controllers.device_configuration_controllers.universal.ssh_controller import (
    SSHGlobalController, SSHAuthController, SSHVtyController
)


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

        self.router_basic_settings_controller = BasicSettingsController(
            self.window.device_config_tab.router_basic_settings,
            self.basic_settings_model
        )
        self.switch_basic_settings_controller = BasicSettingsController(
            self.window.device_config_tab.switch_basic_settings,
            self.basic_settings_model
        )

        self.telnet_auth_model = TelnetAuthModel(self.session_manager)
        self.telnet_vty_model = TelnetVtyModel(self.session_manager)

        self.router_telnet_auth_controller = TelnetAuthController(
            self.window.device_config_tab.router_telnet_view.auth_section,
            self.telnet_auth_model
        )
        self.router_telnet_vty_controller = TelnetVtyController(
            self.window.device_config_tab.router_telnet_view.vty_section,
            self.telnet_vty_model
        )

        self.switch_telnet_auth_controller = TelnetAuthController(
            self.window.device_config_tab.switch_telnet_view.auth_section,
            self.telnet_auth_model
        )
        self.switch_telnet_vty_controller = TelnetVtyController(
            self.window.device_config_tab.switch_telnet_view.vty_section,
            self.telnet_vty_model
        )

        self.ssh_global_model = SSHGlobalModel(self.session_manager)
        self.ssh_auth_model = SSHAuthModel(self.session_manager)
        self.ssh_vty_model = SSHVtyModel(self.session_manager)

        self.router_ssh_global_controller = SSHGlobalController(
            self.window.device_config_tab.router_ssh_view.global_section,
            self.ssh_global_model
        )
        self.router_ssh_auth_controller = SSHAuthController(
            self.window.device_config_tab.router_ssh_view.auth_section,
            self.ssh_auth_model
        )
        self.router_ssh_vty_controller = SSHVtyController(
            self.window.device_config_tab.router_ssh_view.vty_section,
            self.ssh_vty_model
        )

        self.switch_ssh_global_controller = SSHGlobalController(
            self.window.device_config_tab.switch_ssh_view.global_section,
            self.ssh_global_model
        )
        self.switch_ssh_auth_controller = SSHAuthController(
            self.window.device_config_tab.switch_ssh_view.auth_section,
            self.ssh_auth_model
        )
        self.switch_ssh_vty_controller = SSHVtyController(
            self.window.device_config_tab.switch_ssh_view.vty_section,
            self.ssh_vty_model
        )

        self.ospf_basic_model = OSPFBasicModel(self.session_manager)
        self.ospf_basic_controller = OSPFBasicController(
            self.window.device_config_tab.ospf_view.basic_config,
            self.ospf_basic_model
        )

        self.ospf_router_id_model = OSPFRouterIdModel(self.session_manager)
        self.ospf_router_id_controller = OSPFRouterIdController(
            self.window.device_config_tab.ospf_view.router_id,
            self.ospf_router_id_model
        )

        self.ospf_passive_int_model = OSPFPassiveInterfaceModel(self.session_manager)
        self.ospf_passive_int_controller = OSPFPassiveInterfaceController(
            self.window.device_config_tab.ospf_view.passive_interfaces,
            self.ospf_passive_int_model
        )

        self.ospf_default_route_model = OSPFDefaultRouteModel(self.session_manager)
        self.ospf_default_route_controller = OSPFDefaultRouteController(
            self.window.device_config_tab.ospf_view.default_route,
            self.ospf_default_route_model
        )

        self._setup_connections()

    def _setup_connections(self):
        """
        Binds UI actions from the window and session manager signals to controller logic.
        """
        self.window.device_config_tab.close_tab_signal.connect(self.handle_session_close)
        self.session_manager.error_occurred.connect(self.window.show_error)

    def handle_session_close(self):
        """
        Safely terminates the active network session and returns to the home view.
        """
        self.session_manager.close_connection()
        self.window.show_home()

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