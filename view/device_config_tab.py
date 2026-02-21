from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QTabWidget, QTreeWidget, QTreeWidgetItem, QStackedWidget, QSplitter,
                               QSpacerItem, QSizePolicy)
from PySide6.QtCore import Signal, Qt

from view.terminal_view import TerminalView
from view.device_configuration_views.ospf_view import (OSPFBasicView, OSPFRouterIdView,
                                                       OSPFPassiveInterfaceView, OSPFDefaultRouteView)

class ConfigSection(QWidget):
    """
    Represents a specific configuration category with a hierarchical navigation tree and a content area.
    """
    def __init__(self, section_items):
        """
        Initializes the configuration section with a nested dictionary of items and their corresponding view widgets.
        """
        super().__init__()
        layout = QHBoxLayout(self)

        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderHidden(True)
        self.nav_tree.setFixedWidth(200)

        self.gray_window = QWidget()
        self.gray_layout = QVBoxLayout(self.gray_window)
        self.gray_layout.setContentsMargins(0, 0, 0, 0)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet("QSplitter::handle { background: transparent; }")

        self.content_stack = QStackedWidget()
        self.widget_map = {}

        for section_name, subsections in section_items.items():
            top_item = QTreeWidgetItem(self.nav_tree, [section_name])
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
        self.nav_tree.expandAll()

        if self.content_stack.count() > 0:
            self.content_stack.setCurrentIndex(0)

        self.terminal_container = QWidget()
        self.terminal_layout = QVBoxLayout(self.terminal_container)
        self.terminal_layout.setContentsMargins(0, 0, 0, 0)
        self.terminal_container.setMinimumWidth(300)

        self.splitter.addWidget(self.content_stack)
        self.splitter.addWidget(self.terminal_container)

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([500, 500])

        self.gray_layout.addWidget(self.splitter)

        layout.addWidget(self.nav_tree)
        layout.addWidget(self.gray_window)

    def _on_item_clicked(self, item, column):
        """
        Updates the stacked widget to show the corresponding configuration view when a tree item is clicked.
        """
        if id(item) in self.widget_map:
            self.content_stack.setCurrentIndex(self.widget_map[id(item)])


class DeviceConfigTab(QWidget):
    """
    Main configuration interface that manages different sections and the terminal instance.
    """
    close_tab_signal = Signal()

    def __init__(self):
        """
        Initializes the device configuration tab, its UI elements, and sub-views.
        """
        super().__init__()
        self.current_connection = None
        self.terminal_widget = None

        self.ospf_view = OSPFBasicView()
        self.ospf_router_id_view = OSPFRouterIdView()
        self.ospf_passive_int_view = OSPFPassiveInterfaceView()
        self.ospf_default_route_view = OSPFDefaultRouteView()

        self._setup_ui()

    def _setup_ui(self):
        """
        Sets up the layout, tabs, sections, and terminal container.
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
            "OSPF": {
                "Basic Config": self.ospf_view,
                "Router ID": self.ospf_router_id_view,
                "Passive Interfaces": self.ospf_passive_int_view,
                "Default Route": self.ospf_default_route_view
            },
            "Interfaces": {
                "IPv4 Settings": None
            },
            "EIGRP": {
                "Basic Config": None
            },
            "Static Routing": {
                "IPv4 Routes": None
            },
            "NAT": {
                "Static NAT": None,
                "Dynamic NAT": None,
                "PAT": None
            },
            "ACLs": {
                "Standard": None,
                "Extended": None
            },
            "DHCP": {
                "Pool Settings": None
            },
            "HSRP": {
                "Basic Config": None
            }
        }
        self.router_section = ConfigSection(router_items)

        switch_items = {
            "VLANs": {
                "Create/Delete": None,
                "Assign Ports": None
            },
            "STP": {
                "Root Bridge": None
            },
            "VTP": {
                "Domain Settings": None
            },
            "Port Security": {
                "Mac Address Config": None
            },
            "EtherChannel": {
                "LACP Settings": None
            },
            "Interfaces": {
                "Port Status": None
            }
        }
        self.switch_section = ConfigSection(switch_items)

        self.terminal_tab_container = QWidget()
        self.terminal_tab_layout = QVBoxLayout(self.terminal_tab_container)

        self.terminal_centering_wrapper = QHBoxLayout()

        self.left_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.right_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.terminal_centering_wrapper.addItem(self.left_spacer)

        self.terminal_inner_container = QWidget()
        self.terminal_inner_layout = QVBoxLayout(self.terminal_inner_container)
        self.terminal_inner_layout.setContentsMargins(0, 0, 0, 0)
        self.terminal_inner_container.setFixedWidth(800)

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
        Handles switching the terminal widget visibility between different tabs.
        """
        if not self.terminal_widget:
            return

        tab_text = self.tabs.tabText(index)
        if tab_text == "Router":
            self.router_section.terminal_layout.addWidget(self.terminal_widget)
            self.terminal_widget.show()
            self.router_section.splitter.setSizes([500, 500])
        elif tab_text == "Switch":
            self.switch_section.terminal_layout.addWidget(self.terminal_widget)
            self.terminal_widget.show()
            self.switch_section.splitter.setSizes([500, 500])
        elif tab_text == "Terminal":
            self.terminal_inner_layout.addWidget(self.terminal_widget)
            self.terminal_widget.show()

    def create_new_terminal(self):
        """
        Creates and registers a new terminal view instance.
        """
        self.cleanup_terminal()
        self.terminal_widget = TerminalView()
        self._on_tab_changed(self.tabs.currentIndex())
        return self.terminal_widget

    def cleanup_terminal(self):
        """
        Removes and destroys the current terminal widget.
        """
        if self.terminal_widget:
            self.terminal_widget.setParent(None)
            self.terminal_widget.deleteLater()
            self.terminal_widget = None

    def set_connection(self, data):
        """
        Updates the UI to display the active connection details.
        """
        self.current_connection = data
        name = data.get('name', '')
        host = data.get('host', '')
        protocol = data.get('protocol', '')

        display_name = name if name else host
        self.info_label.setText(f"Connected to: {display_name} ({protocol})")