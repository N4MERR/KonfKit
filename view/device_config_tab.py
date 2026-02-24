"""
Main configuration view orchestrating router, switch, and terminal tab integration.
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QTabWidget, QTreeWidget, QTreeWidgetItem, QStackedWidget, QSplitter,
                               QSpacerItem, QSizePolicy)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from view.terminal_view import TerminalView
from view.device_configuration_views.ospf_view import (OSPFBasicView, OSPFRouterIdView,
                                                       OSPFPassiveInterfaceView, OSPFDefaultRouteView)
from view.device_configuration_views.basic_settings_view import BasicSettingsView


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

        self.restore_terminal_btn = QPushButton("◀")
        self.restore_terminal_btn.setToolTip("Restore Terminal")
        self.restore_terminal_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: #a0a0a0;
                border: none;
                border-left: 1px solid #444444;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3b3b3b;
                color: white;
            }
        """)
        self.restore_terminal_btn.setFixedWidth(24)
        self.restore_terminal_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.restore_terminal_btn.hide()
        self.restore_terminal_btn.clicked.connect(self._restore_terminal)

        self.content_stack = QStackedWidget()
        self.content_stack.setMinimumWidth(450)
        self.widget_map = {}

        for section_name, subsections in section_items.items():
            top_item = QTreeWidgetItem(self.nav_tree, [section_name])
            top_item.setFlags(top_item.flags() & ~Qt.ItemIsSelectable)

            font = QFont()
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

        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([600, 400])
        self.splitter.splitterMoved.connect(self._on_splitter_moved)

        self.gray_layout.addWidget(self.splitter)
        self.gray_layout.addWidget(self.restore_terminal_btn)

        layout.addWidget(self.nav_tree)
        layout.addWidget(self.gray_window)

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
        Displays the restore button if the terminal is completely collapsed.
        """
        sizes = self.splitter.sizes()
        if len(sizes) > 1 and sizes[1] == 0:
            self.restore_terminal_btn.show()
        else:
            self.restore_terminal_btn.hide()

    def _restore_terminal(self):
        """
        Instantly resizes the terminal to a visible default size when the restore button is clicked.
        """
        sizes = self.splitter.sizes()
        total_width = sum(sizes)
        term_width = 400 if total_width > 850 else int(total_width / 3)

        self.splitter.setSizes([total_width - term_width, term_width])
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

        self.base_settings_view = BasicSettingsView()
        self.ospf_view = OSPFBasicView()
        self.ospf_router_id_view = OSPFRouterIdView()
        self.ospf_passive_int_view = OSPFPassiveInterfaceView()
        self.ospf_default_route_view = OSPFDefaultRouteView()

        self._setup_ui()

    def _setup_ui(self):
        """
        Sets up the UI structure with System section expanded and others collapsed.
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
            "System": {
                "Base Settings": self.base_settings_view
            },
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

        self.router_section.nav_tree.collapseAll()
        system_category = self.router_section.nav_tree.topLevelItem(0)
        if system_category:
            system_category.setExpanded(True)
            if system_category.childCount() > 0:
                self.router_section.nav_tree.setCurrentItem(system_category.child(0))
                self.router_section.content_stack.setCurrentIndex(0)

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
        self.switch_section.nav_tree.collapseAll()

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