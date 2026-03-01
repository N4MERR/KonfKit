from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QComboBox, QCheckBox, QLineEdit,
                               QGroupBox)

from view.terminal_view import TerminalView


class PasswordResetTab(QWidget):
    """
    UI Tab for managing Cisco device password resets via serial connection.
    """

    def __init__(self):
        """
        Initializes the password resetter tab UI and connections.
        """
        super().__init__()
        self._setup_ui()
        self._connect_ui_logic()

    def _setup_ui(self):
        """
        Sets up the internal UI components and layouts adapting to the OS theme.
        """
        self.main_layout = QVBoxLayout(self)
        columns_layout = QHBoxLayout()

        self.groupBox_connection = QGroupBox("Connection Settings")
        self.groupBox_connection.setMaximumWidth(280)
        self.groupBox_connection.setStyleSheet("""
            QGroupBox {
                background-color: transparent;
                border: 2px solid rgba(128, 128, 128, 0.3);
                border-radius: 8px;
                margin-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        left_vbox = QVBoxLayout(self.groupBox_connection)

        self.status_layout = QHBoxLayout()
        self.status_led = QLabel("●")
        self.status_led.setStyleSheet("color: #d32f2f; font-size: 14pt; background: transparent;")
        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("background: transparent;")
        self.status_layout.addWidget(self.status_led)
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addStretch()
        left_vbox.addLayout(self.status_layout)

        self.serial_line_input = QComboBox()
        self.serial_line_input.setPlaceholderText("Select COM Port...")
        self.refresh_ports_button = QPushButton("Refresh")
        self.refresh_ports_button.setFixedSize(70, 24)
        self.refresh_ports_button.setStyleSheet(
            "QPushButton { background-color: #6c757d; color: white; border-radius: 4px; border: none; font-weight: bold; } "
            "QPushButton:hover { background-color: #5a6268; }"
        )

        port_hbox = QHBoxLayout()
        port_hbox.addWidget(self.serial_line_input)
        port_hbox.addWidget(self.refresh_ports_button)

        lbl_com = QLabel("COM Port")
        lbl_com.setStyleSheet("background: transparent;")
        left_vbox.addWidget(lbl_com)
        left_vbox.addLayout(port_hbox)

        lbl_baud = QLabel("Baud Rate")
        lbl_baud.setStyleSheet("background: transparent;")
        left_vbox.addWidget(lbl_baud)
        self.baud_rate_input = QComboBox()
        self.baud_rate_input.setPlaceholderText("Select Baud Rate...")
        left_vbox.addWidget(self.baud_rate_input)

        lbl_device = QLabel("Device Model")
        lbl_device.setStyleSheet("background: transparent;")
        left_vbox.addWidget(lbl_device)
        self.device_selector = QComboBox()
        self.device_selector.setPlaceholderText("Select Device Model...")
        left_vbox.addWidget(self.device_selector)

        connect_hbox = QHBoxLayout()
        connect_hbox.addStretch()
        self.connect_button = QPushButton("Connect")
        self.connect_button.setFixedSize(100, 28)
        self.connect_button.setStyleSheet(
            "QPushButton { background-color: #0078d4; color: white; font-weight: bold; border-radius: 4px; border: none; } "
            "QPushButton:hover { background-color: #005a9e; }"
        )
        connect_hbox.addWidget(self.connect_button)
        left_vbox.addLayout(connect_hbox)

        left_vbox.addStretch()

        self.groupBox_options = QGroupBox("Configuration Actions")
        self.groupBox_options.setStyleSheet("""
            QGroupBox {
                background-color: transparent;
                border: 2px dashed rgba(128, 128, 128, 0.3);
                border-radius: 8px;
                margin-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
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
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet(
            "QPushButton { background-color: #d32f2f; color: white; font-weight: bold; border-radius: 4px; border: none; } "
            "QPushButton:hover { background-color: #b71c1c; } "
            "QPushButton:disabled { background-color: rgba(211, 47, 47, 0.4); }"
        )

        self.confirm_button = QPushButton("START")
        self.confirm_button.setFixedSize(100, 40)
        self.confirm_button.setEnabled(False)
        self.confirm_button.setToolTip("Please connect to a device first")
        self.confirm_button.setStyleSheet(
            "QPushButton { background-color: #28a745; color: white; font-weight: bold; border-radius: 4px; border: none; } "
            "QPushButton:hover { background-color: #218838; } "
            "QPushButton:disabled { background-color: rgba(40, 167, 69, 0.4); }"
        )

        buttons_container.addWidget(self.stop_button)
        buttons_container.addWidget(self.confirm_button)
        self.main_layout.addLayout(buttons_container)

    def _connect_ui_logic(self):
        """
        Connects dynamic logic for toggling UI elements.
        """
        self.set_new_privileged_exec_mode_password_toggle.toggled.connect(self._on_set_enable_toggled)
        self.new_line_console_password_toggle.toggled.connect(self._on_set_console_toggled)
        self.remove_privileged_exec_mode_toggle.toggled.connect(self._on_remove_enable_toggled)
        self.remove_line_console_password_toggle.toggled.connect(self._on_remove_console_toggled)

    def _on_set_enable_toggled(self, checked):
        """
        Handles state change when setting new enable password is toggled.
        """
        if checked: self.remove_privileged_exec_mode_toggle.setChecked(True)
        self.privileged_exec_mode_password_input.setEnabled(checked)
        self.encrypt_privileged_exec_mode_password_toggle.setEnabled(checked)

    def _on_set_console_toggled(self, checked):
        """
        Handles state change when setting new console password is toggled.
        """
        if checked: self.remove_line_console_password_toggle.setChecked(True)
        self.line_console_password_input.setEnabled(checked)

    def _on_remove_enable_toggled(self, checked):
        """
        Handles state change when removing enable password is toggled.
        """
        if not checked: self.set_new_privileged_exec_mode_password_toggle.setChecked(False)

    def _on_remove_console_toggled(self, checked):
        """
        Handles state change when removing console password is toggled.
        """
        if not checked: self.new_line_console_password_toggle.setChecked(False)

    def update_status_led(self, connected: bool):
        """
        Updates the status indicator LED based on connection state.
        """
        if connected:
            self.status_led.setStyleSheet("color: #28a745; font-size: 14pt; background: transparent;")
            self.status_label.setText("Connected")
            self.connect_button.setText("Disconnect")
            self.confirm_button.setEnabled(True)
            self.confirm_button.setToolTip("")
        else:
            self.status_led.setStyleSheet("color: #d32f2f; font-size: 14pt; background: transparent;")
            self.status_label.setText("Disconnected")
            self.connect_button.setText("Connect")
            self.confirm_button.setEnabled(False)
            self.confirm_button.setToolTip("Please connect to a device first")

    def get_terminal(self):
        """
        Returns the terminal view component.
        """
        return self.terminal

    def get_connect_button(self):
        """
        Returns the connect button component.
        """
        return self.connect_button

    def get_confirm_button(self):
        """
        Returns the confirm button component.
        """
        return self.confirm_button

    def get_stop_button(self):
        """
        Returns the stop button component.
        """
        return self.stop_button

    def get_refresh_button(self):
        """
        Returns the refresh ports button component.
        """
        return self.refresh_ports_button

    def set_device_list(self, items):
        """
        Sets the list of selectable devices in the UI.
        """
        self.device_selector.clear()
        self.device_selector.addItems(items)
        self.device_selector.setCurrentIndex(-1)

    def set_baud_rate_list(self, rates):
        """
        Sets the list of selectable baud rates in the UI.
        """
        self.baud_rate_input.clear()
        self.baud_rate_input.addItems([str(r) for r in rates])
        self.baud_rate_input.setCurrentIndex(-1)

    def set_port_list(self, ports):
        """
        Sets the list of selectable COM ports in the UI.
        """
        self.serial_line_input.clear()
        self.serial_line_input.addItems(ports)
        self.serial_line_input.setCurrentIndex(-1)

    def get_port(self):
        """
        Returns the currently selected port.
        """
        return self.serial_line_input.currentText()

    def get_baud_rate(self):
        """
        Returns the currently selected baud rate.
        """
        val = self.baud_rate_input.currentText()
        return int(val) if val.isdigit() else 0

    def get_selected_device(self):
        """
        Returns the currently selected device model.
        """
        return self.device_selector.currentText()

    def is_remove_enable_checked(self):
        """
        Returns whether remove enable password is checked.
        """
        return self.remove_privileged_exec_mode_toggle.isChecked()

    def is_remove_console_checked(self):
        """
        Returns whether remove console password is checked.
        """
        return self.remove_line_console_password_toggle.isChecked()

    def is_set_new_enable_checked(self):
        """
        Returns whether set new enable password is checked.
        """
        return self.set_new_privileged_exec_mode_password_toggle.isChecked()

    def is_set_new_console_checked(self):
        """
        Returns whether set new console password is checked.
        """
        return self.new_line_console_password_toggle.isChecked()

    def is_encrypt_enable_checked(self):
        """
        Returns whether encrypt enable password is checked.
        """
        return self.encrypt_privileged_exec_mode_password_toggle.isChecked()

    def get_new_enable_pass(self):
        """
        Returns the new enable password text.
        """
        return self.privileged_exec_mode_password_input.text()

    def get_new_console_pass(self):
        """
        Returns the new console password text.
        """
        return self.line_console_password_input.text()

    def set_ui_locked(self, locked):
        """
        Locks or unlocks the UI elements based on processing state.
        """
        self.groupBox_connection.setEnabled(not locked)
        self.groupBox_options.setEnabled(not locked)
        self.confirm_button.setEnabled(not locked if self.status_label.text() == "Connected" else False)
        self.stop_button.setEnabled(locked)