from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal

class AddConnectionCard(QPushButton):
    """
    A square dashed card used to trigger the addition of a new connection.
    """
    def __init__(self, protocol_name):
        super().__init__()
        self.setFixedSize(160, 120)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px dashed #444;
                border-radius: 8px;
            }
            QPushButton:hover { border-color: #0078d4; }
        """)

        layout = QVBoxLayout(self)
        plus_icon = QLabel("+")
        plus_icon.setStyleSheet("color: #666; font-size: 32px; font-weight: bold; background: transparent;")
        plus_icon.setAlignment(Qt.AlignCenter)

        text_label = QLabel(f"Add {protocol_name}")
        text_label.setStyleSheet("color: #666; font-size: 9pt; font-weight: bold; background: transparent;")
        text_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(plus_icon)
        layout.addWidget(text_label)

class ConnectionRow(QWidget):
    """
    A horizontal row with left-aligned connections and manual arrow navigation.
    """
    add_requested = Signal()
    connect_requested = Signal(dict)

    def __init__(self, title, protocol):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 10, 0, 10)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 11pt; font-weight: bold; color: #0078d4; border: none;")
        self.layout.addWidget(self.title_label)

        self.nav_layout = QHBoxLayout()

        self.left_btn = QPushButton("<")
        self.left_btn.setFixedSize(30, 120)
        self.left_btn.setCursor(Qt.PointingHandCursor)
        self.left_btn.setStyleSheet("background-color: #252525; color: white; border-radius: 4px;")

        self.right_btn = QPushButton(">")
        self.right_btn.setFixedSize(30, 120)
        self.right_btn.setCursor(Qt.PointingHandCursor)
        self.right_btn.setStyleSheet("background-color: #252525; color: white; border-radius: 4px;")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFixedHeight(140)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent; border: none;")
        self.container_layout = QHBoxLayout(self.container)
        self.container_layout.setContentsMargins(5, 5, 5, 5)
        self.container_layout.setSpacing(15)
        self.container_layout.setAlignment(Qt.AlignLeft)
        self.scroll_area.setWidget(self.container)

        self.add_card = AddConnectionCard(protocol)
        self.add_card.clicked.connect(self.add_requested.emit)
        self.container_layout.addWidget(self.add_card)

        self.nav_layout.addWidget(self.left_btn)
        self.nav_layout.addWidget(self.scroll_area)
        self.nav_layout.addWidget(self.right_btn)
        self.layout.addLayout(self.nav_layout)

        self.left_btn.clicked.connect(self._scroll_left)
        self.right_btn.clicked.connect(self._scroll_right)

    def _scroll_left(self):
        bar = self.scroll_area.horizontalScrollBar()
        bar.setValue(max(bar.value() - 200, bar.minimum()))

    def _scroll_right(self):
        bar = self.scroll_area.horizontalScrollBar()
        bar.setValue(min(bar.value() + 200, bar.maximum()))

    def update_connections(self, connections):
        """
        Rebuilds the row while keeping the 'Add' card at index 0.
        """
        while self.container_layout.count() > 1:
            item = self.container_layout.takeAt(1)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for conn in connections:
            card = QPushButton(conn.get('name', 'Unnamed'))
            card.setFixedSize(160, 120)
            card.setStyleSheet("""
                QPushButton {
                    background-color: #2d2d2d;
                    border: 1px solid #3d3d3d;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #3d3d3d; border-color: #0078d4; }
            """)
            card.clicked.connect(lambda checked=False, c=conn: self.connect_requested.emit(c))
            self.container_layout.addWidget(card)

        self.container_layout.addStretch()

class ConnectionManagerTab(QWidget):
    """
    Unified container for connection rows using a shared borderless background.
    """
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(0)

        self.shared_container = QFrame()
        self.shared_container.setStyleSheet("""
            QFrame#SharedRowContainer {
                background-color: #1e1e1e;
                border: none;
                border-radius: 10px;
            }
        """)
        self.shared_container.setObjectName("SharedRowContainer")
        self.container_layout = QVBoxLayout(self.shared_container)
        self.container_layout.setContentsMargins(15, 10, 15, 10)
        self.container_layout.setSpacing(0)

        self.serial_row = ConnectionRow("Serial Connections", "Serial")
        self.ssh_row = ConnectionRow("SSH Connections", "SSH")
        self.telnet_row = ConnectionRow("Telnet Connections", "Telnet")

        self.container_layout.addWidget(self.serial_row)
        self.container_layout.addWidget(self._create_separator())
        self.container_layout.addWidget(self.ssh_row)
        self.container_layout.addWidget(self._create_separator())
        self.container_layout.addWidget(self.telnet_row)

        self.main_layout.addWidget(self.shared_container)
        self.main_layout.addStretch()

    def _create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Plain)
        line.setStyleSheet("background-color: #2d2d2d; max-height: 1px; border: none;")
        return line

    def update_list(self, all_connections):
        """
        Synchronizes all protocol rows with the provided connection data list.
        """
        self.serial_row.update_connections([c for c in all_connections if c.get('protocol') == 'Serial'])
        self.ssh_row.update_connections([c for c in all_connections if c.get('protocol') == 'SSH'])
        self.telnet_row.update_connections([c for c in all_connections if c.get('protocol') == 'Telnet'])