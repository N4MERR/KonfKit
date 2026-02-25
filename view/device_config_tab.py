"""
Main configuration view orchestrating router, switch, and terminal tab integration.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QTabWidget, QTreeWidget, QTreeWidgetItem, QStackedWidget, QSplitter,
                               QSpacerItem, QSizePolicy)
from PySide6.QtCore import Signal, Qt

from view.device_configuration_views.switch.vlan_view import VLANView
from view.terminal_view import TerminalView
from view.device_configuration_views.router.ospf_view import OSPFView
from view.device_configuration_views.universal.basic_settings_view import BasicSettingsView
from view.device_configuration_views.universal.telnet_view import TelnetView
from view.device_configuration_views.universal.ssh_view import SSHView


class ConfigSection(QWidget):
    """
    A widget representing a configuration section with a sidebar navigation tree and content stack.
    """

    def __init__(self, section_items):
        """
        Initializes the navigation tree and the stacked widget for the configuration views.
        """
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderHidden(True)
        self.nav_tree.setFixedWidth(250)

        self.nav_tree.setStyleSheet("""
            QTreeWidget {
                background-color: transparent;
                border: none;
                border-right: 2px solid #444444;
                outline: none;
                show-decoration-selected: 0;
            }
            QTreeWidget:focus {
                outline: none;
            }
            QTreeWidget::item {
                min-height: 40px;
                border-bottom: 1px solid #555555;
                border-left: 4px solid transparent;
                margin: 0px;
                padding: 0px;
                outline: none;
            }
            QTreeWidget::item:hover {
                background-color: transparent;
                border-bottom: 1px solid white;
            }
            QTreeWidget::item:selected {
                background-color: #2d2d2d;
                border-bottom: 1px solid #555555;
                border-left: 4px solid #0078d4;
                color: white;
                outline: none;
            }
        """)

        self.gray_window = QWidget()
        self.gray_layout = QHBoxLayout(self.gray_window)
        self.gray_layout.setContentsMargins(0, 0, 0, 0)
        self.gray_layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet("QSplitter::handle { background: #444444; width: 2px; }")

        self.restore_terminal_btn = QPushButton("<", self.gray_window)
        self.restore_terminal_btn.setToolTip("Restore Terminal")
        self.restore_terminal_btn.setFixedWidth(20)
        self.restore_terminal_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: #4fc1ff;
                border: 1px solid #444444;
                border-right: none;
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
                font-family: Arial, sans-serif;
                font-size: 14px;
                font-weight: bold;
                padding-bottom: 2px;
            }
            QPushButton:hover { background-color: #3b3b3b; color: white; }
        """)
        self.restore_terminal_btn.hide()
        self.restore_terminal_btn.clicked.connect(self._restore_terminal)

        self.content_stack = QStackedWidget()
        self.content_stack.setMinimumWidth(450)
        self.widget_map = {}

        for section_name, subsections in section_items.items():
            top_item = QTreeWidgetItem(self.nav_tree, [section_name])
            top_item.setFlags(top_item.flags() & ~Qt.ItemIsSelectable)

            font = self.font()
            font.setBold(True)
            font.setPointSize(11)
            top_item.setFont(0, font)

            for sub_name, widget in subsections.items():
                sub_item = QTreeWidgetItem(top_item, [sub_name])
                if widget is not None:
                    self.content_stack.addWidget(widget)
                else:
                    page = QWidget()
                    page_layout = QVBoxLayout(page)
                    title_label = QLabel(f"{section_name} - {sub_name} Configuration")
                    title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
                    title_label.setAlignment(Qt.AlignCenter)
                    page_layout.addWidget(title_label)
                    page_layout.addStretch()
                    self.content_stack.addWidget(page)

                self.widget_map[id(sub_item)] = self.content_stack.count() - 1

        self.nav_tree.itemClicked.connect(self._on_item_clicked)

        if self.content_stack.count() > 0:
            self.content_stack.setCurrentIndex(0)

        self.terminal_container = QWidget()
        self.terminal_layout = QVBoxLayout(self.terminal_container)
        self.terminal_layout.setContentsMargins(0, 0, 0, 38)
        self.terminal_container.setMinimumWidth(0)

        self.splitter.addWidget(self.content_stack)
        self.splitter.addWidget(self.terminal_container)

        self.splitter.setCollapsible(0, False)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([600, 400])
        self.splitter.splitterMoved.connect(self._on_splitter_moved)

        self.gray_layout.addWidget(self.splitter)
        layout.addWidget(self.nav_tree)
        layout.addWidget(self.gray_window)

    def resizeEvent(self, event):
        """
        Keeps the floating restore button anchored to the right edge.
        """
        super().resizeEvent(event)
        btn_w = self.restore_terminal_btn.width()
        btn_h = 60
        self.restore_terminal_btn.setGeometry(
            self.gray_window.width() - btn_w,
            (self.gray_window.height() - btn_h) // 2,
            btn_w,
            btn_h
        )

    def _on_item_clicked(self, item, column):
        """
        Handles navigation item clicks to switch content or expand categories.
        """
        if item.childCount() > 0:
            item.setExpanded(not item.isExpanded())
        elif id(item) in self.widget_map:
            self.content_stack.setCurrentIndex(self.widget_map[id(item)])

    def _on_splitter_moved(self, pos, index):
        """
        Checks if terminal is collapsed and reveals the floating toggle.
        """
        sizes = self.splitter.sizes()
        if len(sizes) > 1 and sizes[1] <= 5:
            self.restore_terminal_btn.show()
            self.restore_terminal_btn.raise_()
        else:
            self.restore_terminal_btn.hide()

    def _restore_terminal(self):
        """
        Springs the terminal back to life.
        """
        total = sum(self.splitter.sizes())
        self.splitter.setSizes([total - 400, 400])
        self.restore_terminal_btn.hide()


class DeviceConfigTab(QWidget):
    """
    Main tab widget for device configuration, containing Router, Switch, and Terminal sub-tabs.
    """
    close_tab_signal = Signal()

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

        self.ospf_view = OSPFView()

        self.vlan_view = VLANView()

        self._setup_ui()

    def _setup_ui(self):
        """
        Sets up the UI structure with sections organized by category.
        """
        layout = QVBoxLayout(self)

        top_bar = QHBoxLayout()
        self.close_btn = QPushButton("Close")
        self.close_btn.setFixedSize(100, 30)
        self.close_btn.clicked.connect(self.close_tab_signal.emit)

        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #0078d4;")

        dummy_spacer = QWidget()
        dummy_spacer.setFixedSize(100, 30)

        top_bar.addWidget(self.close_btn)
        top_bar.addStretch()
        top_bar.addWidget(self.info_label)
        top_bar.addStretch()
        top_bar.addWidget(dummy_spacer)

        layout.addLayout(top_bar)

        self.tabs = QTabWidget()

        router_items = {
            "System Setup": {
                "General Settings": self.router_basic_settings
            },
            "SSH": {
                "Global Settings": self.router_ssh_view.global_section,
                "Authentication": self.router_ssh_view.auth_section,
                "VTY Lines": self.router_ssh_view.vty_section
            },
            "Telnet": {
                "Authentication": self.router_telnet_view.auth_section,
                "VTY Lines": self.router_telnet_view.vty_section
            },
            "OSPF": {
                "Basic Config": self.ospf_view.basic_config,
                "Router ID": self.ospf_view.router_id,
                "Passive Interfaces": self.ospf_view.passive_interfaces,
                "Default Route": self.ospf_view.default_route
            }
        }
        self.router_section = ConfigSection(router_items)

        self.router_section.nav_tree.collapseAll()
        router_system_category = self.router_section.nav_tree.topLevelItem(0)
        if router_system_category:
            router_system_category.setExpanded(True)
            if router_system_category.childCount() > 0:
                self.router_section.nav_tree.setCurrentItem(router_system_category.child(0))
                self.router_section.content_stack.setCurrentIndex(0)

        switch_items = {
            "System Setup": {
                "General Settings": self.switch_basic_settings
            },
            "SSH": {
                "Global Settings": self.switch_ssh_view.global_section,
                "Authentication": self.switch_ssh_view.auth_section,
                "VTY Lines": self.switch_ssh_view.vty_section
            },
            "Telnet": {
                "Authentication": self.switch_telnet_view.auth_section,
                "VTY Lines": self.switch_telnet_view.vty_section
            },
            "VLAN": {
                "VLAN Database": self.vlan_view
            }
        }
        self.switch_section = ConfigSection(switch_items)

        self.switch_section.nav_tree.collapseAll()
        switch_system_category = self.switch_section.nav_tree.topLevelItem(0)
        if switch_system_category:
            switch_system_category.setExpanded(True)
            if switch_system_category.childCount() > 0:
                self.switch_section.nav_tree.setCurrentItem(switch_system_category.child(0))
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
        self.terminal_inner_container.setMinimumWidth(900)
        self.terminal_inner_container.setMaximumWidth(1200)

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
        name = data.get('name', '')
        host = data.get('host', '')
        protocol = data.get('protocol', '')
        display_name = name if name else host
        self.info_label.setText(f"Connected to: {display_name} ({protocol})")