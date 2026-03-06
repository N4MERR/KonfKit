from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTabWidget,QSpacerItem, QSizePolicy
from PySide6.QtCore import Signal, Qt

from view.config_tab.config_section import ConfigSection
from view.device_configuration_views.switch.vlan_view import VLANView
from view.terminal_view import TerminalView
from view.device_configuration_views.router.ospf_view import OSPFView
from view.device_configuration_views.router.dhcp_view import DHCPView
from view.device_configuration_views.universal.basic_settings_view import BasicSettingsView
from view.device_configuration_views.universal.telnet_view import TelnetView
from view.device_configuration_views.universal.ssh_view import SSHView
from view.device_configuration_views.router.router_interface_view import RouterInterfaceView


class DeviceConfigTab(QWidget):
    """
    Main tab widget for device configuration, containing Router, Switch, and Terminal sub-tabs.
    """
    close_tab_signal = Signal()
    reconnect_signal = Signal()

    def __init__(self):
        """
        Initializes the configuration tab views and layouts.
        """
        super().__init__()
        self.current_connection = None
        self.terminal_widget = None

        self.router_basic_settings = BasicSettingsView()
        self.switch_basic_settings = BasicSettingsView()

        self.router_telnet_view = TelnetView()
        self.switch_telnet_view = TelnetView()

        self.router_ssh_view = SSHView()
        self.switch_ssh_view = SSHView()

        self.router_interface_view = RouterInterfaceView()

        self.ospf_view = OSPFView()
        self.dhcp_view = DHCPView()

        self.vlan_view = VLANView()

        self._setup_ui()

    def _setup_ui(self):
        """
        Sets up the UI structure with sections organized by category.
        """
        layout = QVBoxLayout(self)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(5, 5, 5, 5)

        self.close_btn = QPushButton("Close")
        self.close_btn.setFixedSize(85, 28)
        self.close_btn.setStyleSheet(
            "QPushButton { background-color: #d32f2f; color: white; font-weight: bold; font-size: 9pt; border-radius: 4px; border: none; } "
            "QPushButton:hover { background-color: #b71c1c; }"
        )
        self.close_btn.clicked.connect(self.close_tab_signal.emit)

        self.reconnect_btn = QPushButton("Reconnect")
        self.reconnect_btn.setFixedSize(85, 28)
        self.reconnect_btn.setStyleSheet(
            "QPushButton { background-color: #0078d4; color: white; font-weight: bold; font-size: 9pt; border-radius: 4px; border: none; } "
            "QPushButton:hover { background-color: #005a9e; }"
        )
        self.reconnect_btn.clicked.connect(self.reconnect_signal.emit)
        self.reconnect_btn.hide()

        left_button_layout = QHBoxLayout()
        left_button_layout.setContentsMargins(0, 0, 0, 0)
        left_button_layout.setSpacing(5)
        left_button_layout.addWidget(self.close_btn)
        left_button_layout.addWidget(self.reconnect_btn)

        self.connection_label = QLabel()
        self.connection_label.setAlignment(Qt.AlignCenter)
        self.connection_label.setStyleSheet("font-size: 13pt; font-weight: bold; color: #0078d4; background: transparent;")

        self.led_indicator = QLabel()
        self.led_indicator.setFixedSize(14, 14)
        self.led_indicator.setStyleSheet("background-color: transparent; border-radius: 7px;")

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 11pt; font-weight: bold; background: transparent;")

        center_status_layout = QVBoxLayout()
        center_status_layout.setSpacing(4)

        connection_row = QHBoxLayout()
        connection_row.setAlignment(Qt.AlignCenter)
        connection_row.addWidget(self.connection_label)

        status_row = QHBoxLayout()
        status_row.setAlignment(Qt.AlignCenter)
        status_row.addWidget(self.led_indicator)
        status_row.addWidget(self.status_label)
        status_row.setSpacing(8)

        center_status_layout.addLayout(connection_row)
        center_status_layout.addLayout(status_row)

        dummy_spacer = QWidget()
        dummy_spacer.setFixedSize(175, 28)

        top_bar.addLayout(left_button_layout)
        top_bar.addStretch()
        top_bar.addLayout(center_status_layout)
        top_bar.addStretch()
        top_bar.addWidget(dummy_spacer)

        layout.addLayout(top_bar)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { 
                border: 1px solid rgba(128, 128, 128, 0.2); 
                border-radius: 4px; 
                background: transparent; 
            }
            QTabBar::tab {
                height: 30px;
                width: 120px;
                font-size: 10pt;
                font-weight: bold;
                margin-top: 2px;
                margin-right: 1px;
                margin-left: 1px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid rgba(128, 128, 128, 0.3);
            }
            QTabBar::tab:selected {
                background-color: rgba(0, 120, 212, 0.1);
                border: 1px solid #0078d4;
                border-bottom: none;
            }
            QTabBar::tab:hover:!selected {
                background-color: rgba(0, 120, 212, 0.05);
            }

            QPushButton[text="Preview"] {
                background-color: #ffe066; 
                color: black; 
                font-weight: bold; 
                border-radius: 4px; 
                border: none; 
                min-height: 28px;
                min-width: 90px;
            }
            QPushButton[text="Preview"]:hover {
                background-color: #ffd54f;
            }
            QPushButton[text="Preview"]:disabled {
                background-color: #e0e0e0;
                color: #a0a0a0;
            }

            QPushButton[text="Apply"] {
                background-color: #0078d4; 
                color: white; 
                font-weight: bold; 
                border-radius: 4px; 
                border: none; 
                min-height: 28px;
                min-width: 90px;
            }
            QPushButton[text="Apply"]:hover {
                background-color: #005a9e;
            }
            QPushButton[text="Apply"]:disabled {
                background-color: #a0a0a0;
            }

            QPushButton[text="Apply Configuration"] {
                background-color: #0078d4; 
                color: white; 
                font-weight: bold; 
                border-radius: 4px; 
                border: none; 
                min-height: 28px;
                min-width: 130px;
            }
            QPushButton[text="Apply Configuration"]:hover {
                background-color: #005a9e;
            }
            QPushButton[text="Apply Configuration"]:disabled {
                background-color: #a0a0a0;
            }
        """)

        router_items = {
            "System Setup": {
                "General Settings": self.router_basic_settings
            },
            "Interfaces": {
                "Physical Interfaces": self.router_interface_view.physical,
                "Subinterfaces": self.router_interface_view.subinterface
            },
            "SSH": {
                "SSH Connection": self.router_ssh_view.global_section,
                "SSH Login": self.router_ssh_view.auth_section
            },
            "Telnet": {
                "Telnet Connection": self.router_telnet_view.connection_section,
                "Telnet Login": self.router_telnet_view.login_section
            },
            "DHCP": {
                "DHCP Server": self.dhcp_view.pool_view,
                "Excluded Addresses": self.dhcp_view.excluded_view
            },
            "OSPF": {
                "Basic Config": self.ospf_view.basic_config,
                "Router ID": self.ospf_view.router_id,
                "Passive Interfaces": self.ospf_view.passive_interfaces,
            }
        }
        self.router_section = ConfigSection(router_items)

        router_system_category = self.router_section.nav_tree.topLevelItem(0)
        if router_system_category:
            router_system_category.setSelected(True)
            self.router_section.nav_tree.setCurrentItem(router_system_category)
            self.router_section.content_stack.setCurrentIndex(0)

        switch_items = {
            "System Setup": {
                "General Settings": self.switch_basic_settings
            },
            "SSH": {
                "Global Settings": self.switch_ssh_view.global_section,
                "Authentication": self.switch_ssh_view.auth_section
            },
            "Telnet": {
                "Telnet Connection": self.switch_telnet_view.connection_section,
                "Telnet Login": self.switch_telnet_view.login_section
            },
            "VLAN": {
                "VLAN Database": self.vlan_view
            }
        }
        self.switch_section = ConfigSection(switch_items)

        switch_system_category = self.switch_section.nav_tree.topLevelItem(0)
        if switch_system_category:
            switch_system_category.setSelected(True)
            self.switch_section.nav_tree.setCurrentItem(switch_system_category)
            self.switch_section.content_stack.setCurrentIndex(0)

        self.terminal_tab_container = QWidget()
        self.terminal_tab_layout = QVBoxLayout(self.terminal_tab_container)
        self.terminal_centering_wrapper = QHBoxLayout()
        self.left_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.right_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.terminal_centering_wrapper.addItem(self.left_spacer)

        self.terminal_inner_container = QWidget()
        self.terminal_inner_layout = QVBoxLayout(self.terminal_inner_container)
        self.terminal_inner_layout.setContentsMargins(0, 0, 0, 0)
        self.terminal_inner_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.terminal_inner_container.setMinimumWidth(800)
        self.terminal_inner_container.setMaximumWidth(1100)

        self.terminal_centering_wrapper.addWidget(self.terminal_inner_container)
        self.terminal_centering_wrapper.addItem(self.right_spacer)
        self.terminal_tab_layout.addLayout(self.terminal_centering_wrapper)

        self.tabs.addTab(self.router_section, "Router")
        self.tabs.addTab(self.switch_section, "Switch")
        self.tabs.addTab(self.terminal_tab_container, "Terminal")
        self.tabs.currentChanged.connect(self._on_tab_changed)

        layout.addWidget(self.tabs)

    def _on_tab_changed(self, index):
        """
        Manages the movement of the single terminal widget between different tabs.
        """
        if not self.terminal_widget:
            return

        tab_text = self.tabs.tabText(index)
        if tab_text == "Router":
            self.router_section.terminal_layout.addWidget(self.terminal_widget)
            self.terminal_widget.show()
        elif tab_text == "Switch":
            self.switch_section.terminal_layout.addWidget(self.terminal_widget)
            self.terminal_widget.show()
        elif tab_text == "Terminal":
            self.terminal_inner_layout.addWidget(self.terminal_widget)
            self.terminal_widget.show()

    def create_new_terminal(self):
        """
        Recreates the terminal view for a fresh connection.
        """
        self.cleanup_terminal()
        self.terminal_widget = TerminalView()
        self._on_tab_changed(self.tabs.currentIndex())
        return self.terminal_widget

    def cleanup_terminal(self):
        """
        Safely removes and deletes the terminal widget.
        """
        if self.terminal_widget:
            self.terminal_widget.setParent(None)
            self.terminal_widget.deleteLater()
            self.terminal_widget = None

    def set_connection(self, data):
        """
        Updates the UI to reflect information about the current connection.
        """
        self.current_connection = data
        self.set_connection_status(True)

    def set_connection_status(self, is_connected):
        """
        Updates the visual status indicator, toggles the reconnect button, and disables action buttons
        while allowing the input fields to remain editable.
        """
        if not self.current_connection:
            return

        name = self.current_connection.get('name', '')
        host = self.current_connection.get('host', '')
        display_name = name if name else host

        self.connection_label.setText(f"Connected to: {display_name}")

        if is_connected:
            self.led_indicator.setStyleSheet(
                "background-color: #4CAF50; border-radius: 7px; border: 1px solid #388E3C;")
            self.status_label.setText("Status: Connected")
            self.status_label.setStyleSheet(
                "font-size: 11pt; font-weight: bold; color: #4CAF50; background: transparent;")
            self.reconnect_btn.hide()
        else:
            self.led_indicator.setStyleSheet(
                "background-color: #F44336; border-radius: 7px; border: 1px solid #D32F2F;")
            self.status_label.setText("Status: Disconnected")
            self.status_label.setStyleSheet(
                "font-size: 11pt; font-weight: bold; color: #F44336; background: transparent;")
            self.reconnect_btn.show()

        for btn in self.findChildren(QPushButton):
            if btn.text() in ["Apply", "Preview", "Apply Configuration", "Load Interfaces"]:
                btn.setEnabled(is_connected)