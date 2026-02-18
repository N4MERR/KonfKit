from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QTabWidget, QListWidget, QStackedWidget, QSplitter)
from PySide6.QtCore import Signal, Qt

from view.terminal_view import TerminalView


class ConfigSection(QWidget):
    """
    Represents a specific configuration category with a navigation list and a content area.
    """
    def __init__(self, items):
        super().__init__()
        layout = QHBoxLayout(self)
        self.nav_list = QListWidget()
        self.nav_list.addItems(items)
        self.nav_list.setFixedWidth(200)

        self.gray_window = QWidget()
        self.gray_layout = QVBoxLayout(self.gray_window)
        self.gray_layout.setContentsMargins(0, 0, 0, 0)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet("QSplitter::handle { background: transparent; }")

        self.content_stack = QStackedWidget()
        for item in items:
            page = QWidget()
            page_layout = QVBoxLayout(page)

            title_label = QLabel(f"{item} Configuration")
            title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
            title_label.setAlignment(Qt.AlignCenter)

            page_layout.addWidget(title_label)
            page_layout.addStretch()
            self.content_stack.addWidget(page)

        self.nav_list.currentRowChanged.connect(self.content_stack.setCurrentIndex)

        if items:
            self.nav_list.setCurrentRow(0)

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

        layout.addWidget(self.nav_list)
        layout.addWidget(self.gray_window)


class DeviceConfigTab(QWidget):
    """
    Main configuration interface that manages different sections and the terminal instance.
    """
    close_tab_signal = Signal()

    def __init__(self):
        super().__init__()
        self.current_connection = None
        self.terminal_widget = None
        self._setup_ui()

    def _setup_ui(self):
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

        self.router_section = ConfigSection(["Interfaces", "OSPF", "EIGRP", "Static Routing", "NAT", "ACLs", "DHCP"])
        self.switch_section = ConfigSection(["VLANs", "STP", "VTP", "Port Security", "EtherChannel", "Interfaces"])

        self.terminal_tab_container = QWidget()
        self.terminal_tab_layout = QVBoxLayout(self.terminal_tab_container)
        self.terminal_tab_layout.setContentsMargins(0, 0, 0, 0)

        self.tabs.addTab(self.router_section, "Router")
        self.tabs.addTab(self.switch_section, "Switch")
        self.tabs.addTab(self.terminal_tab_container, "Terminal")

        self.tabs.currentChanged.connect(self._on_tab_changed)

        layout.addWidget(self.tabs)

    def _on_tab_changed(self, index):
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
            self.terminal_tab_layout.addWidget(self.terminal_widget)
            self.terminal_widget.show()

    def create_new_terminal(self):
        self.cleanup_terminal()
        self.terminal_widget = TerminalView()
        self._on_tab_changed(self.tabs.currentIndex())
        return self.terminal_widget

    def cleanup_terminal(self):
        if self.terminal_widget:
            self.terminal_widget.setParent(None)
            self.terminal_widget.deleteLater()
            self.terminal_widget = None

    def set_connection(self, data):
        self.current_connection = data
        name = data.get('name', '')
        host = data.get('host', '')
        protocol = data.get('protocol', '')

        display_name = name if name else host
        self.info_label.setText(f"Connected to: {display_name} ({protocol})")