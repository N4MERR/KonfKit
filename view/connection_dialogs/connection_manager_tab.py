from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QScrollArea, QFrame, QToolButton, QMenu)
from PySide6.QtCore import Qt, Signal


class AddConnectionCard(QPushButton):
    """
    UI element for adding a new connection.
    """

    def __init__(self, protocol_name):
        """
        Initializes the add connection card with adaptable styling.
        """
        super().__init__()
        self.setFixedSize(160, 120)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                border: 2px dashed rgba(128, 128, 128, 0.4);
                border-radius: 8px;
                background-color: transparent;
            }
            QPushButton:hover { 
                border-color: #0078d4; 
                background-color: rgba(0, 120, 212, 0.05); 
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        plus_icon = QLabel("+")
        plus_icon.setStyleSheet("QLabel { font-size: 32px; font-weight: bold; background: transparent; border: none; }")
        plus_icon.setAlignment(Qt.AlignCenter)

        text_label = QLabel(f"Add {protocol_name} connection")
        text_label.setStyleSheet("QLabel { font-size: 9pt; font-weight: bold; background: transparent; border: none; }")
        text_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(plus_icon)
        layout.addWidget(text_label)


class ConnectionCard(QFrame):
    """
    UI element representing an individual connection profile.
    """
    connect_requested = Signal(dict)
    edit_requested = Signal(dict)
    delete_requested = Signal(dict)

    def __init__(self, conn, parent=None):
        """
        Initializes the individual connection card display.
        """
        super().__init__(parent)
        self.conn = conn
        self.setFixedSize(160, 120)
        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet("""
            ConnectionCard {
                border: 1px solid rgba(128, 128, 128, 0.4);
                border-radius: 8px;
                background-color: transparent;
            }
            ConnectionCard:hover { 
                border: 2px solid #0078d4; 
                background-color: rgba(0, 120, 212, 0.05); 
            }
            QLabel { 
                font-weight: bold; 
                border: none; 
                background: transparent; 
            }
            QToolButton { 
                border: none; 
                background: transparent; 
                font-size: 18px; 
                font-weight: bold; 
            }
            QToolButton:hover { 
                color: #0078d4; 
            }
            QToolButton::menu-indicator { 
                image: none; 
            }
        """)

        self.options_btn = QToolButton(self)
        self.options_btn.setText("⋮")
        self.options_btn.setPopupMode(QToolButton.InstantPopup)
        self.options_btn.setCursor(Qt.ArrowCursor)
        self.options_btn.setGeometry(135, 5, 20, 25)

        self.menu = QMenu(self)

        connect_action = self.menu.addAction("Connect")
        edit_action = self.menu.addAction("Edit")
        delete_action = self.menu.addAction("Delete")

        connect_action.triggered.connect(lambda: self.connect_requested.emit(self.conn))
        edit_action.triggered.connect(lambda: self.edit_requested.emit(self.conn))
        delete_action.triggered.connect(lambda: self.delete_requested.emit(self.conn))

        self.options_btn.setMenu(self.menu)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setAlignment(Qt.AlignCenter)

        name_label = QLabel(self.conn.get('name', 'Unnamed'))
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

    def mousePressEvent(self, event):
        """
        Handles mouse press logic to emit connection requests.
        """
        if event.button() == Qt.LeftButton:
            self.connect_requested.emit(self.conn)
        super().mousePressEvent(event)


class ConnectionRow(QWidget):
    """
    A horizontal row containing connection cards for a specific protocol.
    """
    add_requested = Signal()
    connect_requested = Signal(dict)
    edit_requested = Signal(dict)
    delete_requested = Signal(dict)

    def __init__(self, title, protocol):
        """
        Initializes the horizontally scrolling row for connection cards.
        """
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 10, 0, 10)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("QLabel { font-size: 11pt; font-weight: bold; background: transparent; }")
        self.layout.addWidget(self.title_label)

        self.nav_layout = QHBoxLayout()

        self.left_btn = QPushButton("<")
        self.left_btn.setFixedSize(30, 120)
        self.left_btn.setCursor(Qt.PointingHandCursor)
        self.left_btn.setStyleSheet(
            "QPushButton { background: transparent; border: 1px solid rgba(128, 128, 128, 0.3); border-radius: 4px; }")

        self.right_btn = QPushButton(">")
        self.right_btn.setFixedSize(30, 120)
        self.right_btn.setCursor(Qt.PointingHandCursor)
        self.right_btn.setStyleSheet(
            "QPushButton { background: transparent; border: 1px solid rgba(128, 128, 128, 0.3); border-radius: 4px; }")

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFixedHeight(140)
        self.scroll_area.setObjectName("RowScrollArea")
        self.scroll_area.setStyleSheet("QScrollArea#RowScrollArea { background: transparent; border: none; }")

        self.container = QWidget()
        self.container.setObjectName("RowContainer")
        self.container.setStyleSheet("QWidget#RowContainer { background: transparent; border: none; }")
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
        """
        Scrolls the row view to the left.
        """
        bar = self.scroll_area.horizontalScrollBar()
        bar.setValue(max(bar.value() - 200, bar.minimum()))

    def _scroll_right(self):
        """
        Scrolls the row view to the right.
        """
        bar = self.scroll_area.horizontalScrollBar()
        bar.setValue(min(bar.value() + 200, bar.maximum()))

    def update_connections(self, connections):
        """
        Updates the displayed connections inside the row container.
        """
        while self.container_layout.count() > 1:
            item = self.container_layout.takeAt(1)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for conn in connections:
            card = ConnectionCard(conn)
            card.connect_requested.connect(self.connect_requested.emit)
            card.edit_requested.connect(self.edit_requested.emit)
            card.delete_requested.connect(self.delete_requested.emit)
            self.container_layout.addWidget(card)

        self.container_layout.addStretch()


class ConnectionManagerTab(QWidget):
    """
    Main tab for managing all connection profiles.
    """
    connect_profile_requested = Signal(dict)
    edit_profile_requested = Signal(dict)
    delete_profile_requested = Signal(dict)

    def __init__(self):
        """
        Initializes the connection manager tab UI adapted to the system theme.
        """
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(0)

        self.shared_container = QFrame()
        self.shared_container.setStyleSheet("""
            QFrame#SharedRowContainer {
                border: 2px solid rgba(128, 128, 128, 0.2);
                border-radius: 12px;
                background-color: transparent;
            }
        """)
        self.shared_container.setObjectName("SharedRowContainer")
        self.container_layout = QVBoxLayout(self.shared_container)
        self.container_layout.setContentsMargins(15, 10, 15, 10)
        self.container_layout.setSpacing(0)

        self.serial_row = ConnectionRow("Serial Connections", "Serial")
        self.ssh_row = ConnectionRow("SSH Connections", "SSH")
        self.telnet_row = ConnectionRow("Telnet Connections", "Telnet")

        self._connect_row_signals(self.serial_row)
        self._connect_row_signals(self.ssh_row)
        self._connect_row_signals(self.telnet_row)

        self.container_layout.addWidget(self.serial_row)
        self.container_layout.addWidget(self._create_separator())
        self.container_layout.addWidget(self.ssh_row)
        self.container_layout.addWidget(self._create_separator())
        self.container_layout.addWidget(self.telnet_row)

        self.main_layout.addWidget(self.shared_container)
        self.main_layout.addStretch()

    def _connect_row_signals(self, row):
        """
        Binds signals from specific row components to tab components.
        """
        row.connect_requested.connect(self.connect_profile_requested.emit)
        row.edit_requested.connect(self.edit_profile_requested.emit)
        row.delete_requested.connect(self.delete_profile_requested.emit)

    def _create_separator(self):
        """
        Creates and returns a horizontal separator line UI element.
        """
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Plain)
        line.setStyleSheet(
            "QFrame { border-bottom: 2px dashed rgba(128, 128, 128, 0.2); max-height: 2px; background: transparent; }")
        return line

    def update_list(self, all_connections):
        """
        Sorts profiles into rows based on the device_type key.
        """
        self.serial_row.update_connections([c for c in all_connections if 'serial' in c.get('device_type', '')])
        self.ssh_row.update_connections([c for c in all_connections if c.get('device_type') == 'cisco_ios'])
        self.telnet_row.update_connections([c for c in all_connections if 'telnet' in c.get('device_type', '')])