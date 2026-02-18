from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QComboBox, QCheckBox, QLineEdit,
                               QGroupBox)

from view.terminal_view import TerminalView


class PasswordResetTab(QWidget):
    """
    UI Tab for managing Cisco device password resets via serial connection.
    """
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._connect_ui_logic()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        columns_layout = QHBoxLayout()

        btn_style_blue = """
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0086f0; }
            QPushButton:pressed { background-color: #005a9e; }
            QPushButton:disabled { background-color: #333333; color: #777777; }
        """
        btn_style_green = btn_style_blue.replace("#0078d4", "#28a745").replace("#0086f0", "#218838").replace("#005a9e", "#1e7e34")
        btn_style_red = btn_style_blue.replace("#0078d4", "#d32f2f").replace("#0086f0", "#f44336").replace("#005a9e", "#b71c1c")

        self.groupBox_connection = QGroupBox("Connection Settings")
        self.groupBox_connection.setMaximumWidth(280)
        left_vbox = QVBoxLayout(self.groupBox_connection)

        self.status_layout = QHBoxLayout()
        self.status_led = QLabel("●")
        self.status_led.setStyleSheet("color: red; font-size: 14pt;")
        self.status_label = QLabel("Disconnected")
        self.status_layout.addWidget(self.status_led)
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addStretch()
        left_vbox.addLayout(self.status_layout)

        self.serial_line_input = QComboBox()
        self.serial_line_input.setPlaceholderText("Select COM Port...")
        self.refresh_ports_button = QPushButton("Refresh")
        self.refresh_ports_button.setFixedSize(70, 24)
        self.refresh_ports_button.setStyleSheet(btn_style_blue)

        port_hbox = QHBoxLayout()
        port_hbox.addWidget(self.serial_line_input)
        port_hbox.addWidget(self.refresh_ports_button)

        left_vbox.addWidget(QLabel("COM Port"))
        left_vbox.addLayout(port_hbox)

        left_vbox.addWidget(QLabel("Baud Rate"))
        self.baud_rate_input = QComboBox()
        self.baud_rate_input.setPlaceholderText("Select Baud Rate...")
        left_vbox.addWidget(self.baud_rate_input)

        left_vbox.addWidget(QLabel("Device Model"))
        self.device_selector = QComboBox()
        self.device_selector.setPlaceholderText("Select Device Model...")
        left_vbox.addWidget(self.device_selector)

        connect_hbox = QHBoxLayout()
        connect_hbox.addStretch()
        self.connect_button = QPushButton("Connect")
        self.connect_button.setFixedSize(100, 28)
        self.connect_button.setStyleSheet(btn_style_blue)
        connect_hbox.addWidget(self.connect_button)
        left_vbox.addLayout(connect_hbox)

        left_vbox.addStretch()

        self.groupBox_options = QGroupBox("Configuration Actions")
        right_vbox = QVBoxLayout(self.groupBox_options)

        self.remove_privileged_exec_mode_toggle = QCheckBox("Remove Enable Password")
        self.set_new_privileged_exec_mode_password_toggle = QCheckBox("Set New Enable Password")
        self.encrypt_privileged_exec_mode_password_toggle = QCheckBox("Encrypt Password (Secret)")

        self.privileged_exec_mode_password_input = QLineEdit()
        self.privileged_exec_mode_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.privileged_exec_mode_password_input.setPlaceholderText("Enter new enable password...")

        self.remove_line_console_password_toggle = QCheckBox("Remove Console Password")
        self.new_line_console_password_toggle = QCheckBox("Set New Console Password")

        self.line_console_password_input = QLineEdit()
        self.line_console_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.line_console_password_input.setPlaceholderText("Enter new console password...")

        self.privileged_exec_mode_password_input.setEnabled(False)
        self.encrypt_privileged_exec_mode_password_toggle.setEnabled(False)
        self.line_console_password_input.setEnabled(False)

        right_vbox.addWidget(self.remove_privileged_exec_mode_toggle)
        right_vbox.addWidget(self.set_new_privileged_exec_mode_password_toggle)
        right_vbox.addWidget(self.encrypt_privileged_exec_mode_password_toggle)
        right_vbox.addWidget(self.privileged_exec_mode_password_input)
        right_vbox.addSpacing(15)
        right_vbox.addWidget(self.remove_line_console_password_toggle)
        right_vbox.addWidget(self.new_line_console_password_toggle)
        right_vbox.addWidget(self.line_console_password_input)
        right_vbox.addStretch()

        columns_layout.addWidget(self.groupBox_connection, 1)
        columns_layout.addWidget(self.groupBox_options, 2)
        self.main_layout.addLayout(columns_layout)

        self.terminal = TerminalView()
        self.main_layout.addWidget(self.terminal)

        buttons_container = QHBoxLayout()
        buttons_container.addStretch()

        self.stop_button = QPushButton("STOP")
        self.stop_button.setFixedSize(100, 40)
        self.stop_button.setStyleSheet(btn_style_red)
        self.stop_button.setEnabled(False)

        self.confirm_button = QPushButton("START")
        self.confirm_button.setFixedSize(100, 40)
        self.confirm_button.setStyleSheet(btn_style_green)
        self.confirm_button.setEnabled(False)
        self.confirm_button.setToolTip("Please connect to a device first")

        buttons_container.addWidget(self.stop_button)
        buttons_container.addWidget(self.confirm_button)
        self.main_layout.addLayout(buttons_container)

    def _connect_ui_logic(self):
        self.set_new_privileged_exec_mode_password_toggle.toggled.connect(self._on_set_enable_toggled)
        self.new_line_console_password_toggle.toggled.connect(self._on_set_console_toggled)
        self.remove_privileged_exec_mode_toggle.toggled.connect(self._on_remove_enable_toggled)
        self.remove_line_console_password_toggle.toggled.connect(self._on_remove_console_toggled)

    def _on_set_enable_toggled(self, checked):
        if checked: self.remove_privileged_exec_mode_toggle.setChecked(True)
        self.privileged_exec_mode_password_input.setEnabled(checked)
        self.encrypt_privileged_exec_mode_password_toggle.setEnabled(checked)

    def _on_set_console_toggled(self, checked):
        if checked: self.remove_line_console_password_toggle.setChecked(True)
        self.line_console_password_input.setEnabled(checked)

    def _on_remove_enable_toggled(self, checked):
        if not checked: self.set_new_privileged_exec_mode_password_toggle.setChecked(False)

    def _on_remove_console_toggled(self, checked):
        if not checked: self.new_line_console_password_toggle.setChecked(False)

    def update_status_led(self, connected: bool):
        if connected:
            self.status_led.setStyleSheet("color: #00FF00; font-size: 14pt;")
            self.status_label.setText("Connected")
            self.connect_button.setText("Disconnect")
            self.confirm_button.setEnabled(True)
            self.confirm_button.setToolTip("")
        else:
            self.status_led.setStyleSheet("color: red; font-size: 14pt;")
            self.status_label.setText("Disconnected")
            self.connect_button.setText("Connect")
            self.confirm_button.setEnabled(False)
            self.confirm_button.setToolTip("Please connect to a device first")

    def get_terminal(self):
        return self.terminal

    def get_connect_button(self):
        return self.connect_button

    def get_confirm_button(self):
        return self.confirm_button

    def get_stop_button(self):
        return self.stop_button

    def get_refresh_button(self):
        return self.refresh_ports_button

    def set_device_list(self, items):
        self.device_selector.clear()
        self.device_selector.addItems(items)
        self.device_selector.setCurrentIndex(-1)

    def set_baud_rate_list(self, rates):
        self.baud_rate_input.clear()
        self.baud_rate_input.addItems([str(r) for r in rates])
        self.baud_rate_input.setCurrentIndex(-1)

    def set_port_list(self, ports):
        self.serial_line_input.clear()
        self.serial_line_input.addItems(ports)
        self.serial_line_input.setCurrentIndex(-1)

    def get_port(self):
        return self.serial_line_input.currentText()

    def get_baud_rate(self):
        val = self.baud_rate_input.currentText()
        return int(val) if val.isdigit() else 0

    def get_selected_device(self):
        return self.device_selector.currentText()

    def is_remove_enable_checked(self):
        return self.remove_privileged_exec_mode_toggle.isChecked()

    def is_remove_console_checked(self):
        return self.remove_line_console_password_toggle.isChecked()

    def is_set_new_enable_checked(self):
        return self.set_new_privileged_exec_mode_password_toggle.isChecked()

    def is_set_new_console_checked(self):
        return self.new_line_console_password_toggle.isChecked()

    def is_encrypt_enable_checked(self):
        return self.encrypt_privileged_exec_mode_password_toggle.isChecked()

    def get_new_enable_pass(self):
        return self.privileged_exec_mode_password_input.text()

    def get_new_console_pass(self):
        return self.line_console_password_input.text()

    def set_ui_locked(self, locked):
        self.groupBox_connection.setEnabled(not locked)
        self.groupBox_options.setEnabled(not locked)
        self.confirm_button.setEnabled(not locked if self.status_label.text() == "Connected" else False)
        self.stop_button.setEnabled(locked)