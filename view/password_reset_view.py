from PySide6.QtWidgets import (QWidget, QGroupBox, QVBoxLayout, QHBoxLayout,
                               QLabel, QComboBox, QPushButton, QCheckBox,
                               QScrollArea, QSizePolicy)
from PySide6.QtCore import Qt, QEvent
from view.terminal_view import TerminalView
from view.device_configuration_views.input_fields.password_field import PasswordField
from view.device_configuration_views.input_fields.port_combobox import PortComboBox
from utils.cisco_devices import Devices


class PasswordResetView(QWidget):
    """
    Standalone user interface for password reset.
    Layout: Connection (Left), Options (Middle), Terminal (Right) with a 2:4:3 spatial ratio.
    """

    def __init__(self):
        """
        Initializes the view structure and disables specific components until connected.
        """
        super().__init__()
        self._setup_ui()
        self._connect_ui_constraints()
        self._set_initial_state()
        self._populate_device_models()

    def _setup_ui(self):
        """
        Assembles the three-column layout utilizing stretch factors for precise alignment.
        Uses structural QGroupBoxes to ensure visual top-alignment across all columns.
        """
        self.main_layout = QHBoxLayout(self)

        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self._setup_connection_ui()

        self.middle_panel = QWidget()
        self.middle_layout = QVBoxLayout(self.middle_panel)
        self.middle_layout.setContentsMargins(0, 0, 0, 0)
        self._setup_fields()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.middle_panel)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setContentsMargins(0, 0, 0, 0)

        self.terminal_container = QGroupBox("Terminal Output")
        self.terminal_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        term_layout = QVBoxLayout(self.terminal_container)
        term_layout.setContentsMargins(0, 5, 0, 0)
        self.terminal_view = TerminalView()
        term_layout.addWidget(self.terminal_view)

        self.main_layout.addWidget(self.left_panel, 2)
        self.main_layout.addWidget(scroll_area, 4)
        self.main_layout.addWidget(self.terminal_container, 3)

    def _setup_connection_ui(self):
        """
        Creates the serial connection settings panel on the left.
        Expands the group box vertically to match the terminal border.
        """
        self.groupBox_connection = QGroupBox("Serial Connection")
        self.groupBox_connection.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(self.groupBox_connection)

        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("color: #d32f2f; font-weight: bold; font-size: 14px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        layout.addSpacing(10)

        layout.addWidget(QLabel("COM Port:"))
        self.port_input = PortComboBox()
        layout.addWidget(self.port_input)

        self.port_error = QLabel()
        self.port_error.setStyleSheet("color: red; font-size: 12px; font-weight: bold;")
        self.port_error.hide()
        layout.addWidget(self.port_error)

        layout.addWidget(QLabel("Baud Rate:"))
        self.baud_rate_input = QComboBox()
        self.baud_rate_input.addItems(["9600", "19200", "38400", "57600", "115200"])
        layout.addWidget(self.baud_rate_input)

        self.baud_error = QLabel()
        self.baud_error.setStyleSheet("color: red; font-size: 12px; font-weight: bold;")
        self.baud_error.hide()
        layout.addWidget(self.baud_error)

        layout.addWidget(QLabel("Device Model:"))
        self.device_selector = QComboBox()
        self.device_selector.setPlaceholderText("Select Device Model...")
        layout.addWidget(self.device_selector)

        self.device_error = QLabel()
        self.device_error.setStyleSheet("color: red; font-size: 12px; font-weight: bold;")
        self.device_error.hide()
        layout.addWidget(self.device_error)

        layout.addSpacing(15)
        self.connect_button = QPushButton("Connect")
        self.connect_button.setMinimumHeight(35)
        layout.addWidget(self.connect_button)

        layout.addStretch()
        self.left_layout.addWidget(self.groupBox_connection)

        self.port_input.installEventFilter(self)
        self.baud_rate_input.installEventFilter(self)
        self.device_selector.installEventFilter(self)

        if hasattr(self.port_input, "currentTextChanged"):
            self.port_input.currentTextChanged.connect(lambda: self.clear_error(self.port_input, self.port_error))
        if hasattr(self.port_input, "currentIndexChanged"):
            self.port_input.currentIndexChanged.connect(lambda: self.clear_error(self.port_input, self.port_error))

        self.baud_rate_input.currentIndexChanged.connect(
            lambda: self.clear_error(self.baud_rate_input, self.baud_error))
        self.device_selector.currentIndexChanged.connect(
            lambda: self.clear_error(self.device_selector, self.device_error))

    def _setup_fields(self):
        """
        Adds standard checkboxes, password fields, and submit button to the middle configuration block.
        Expands the group box vertically to match the terminal border.
        """
        self.groupBox_config = QGroupBox("Reset Configuration")
        self.groupBox_config.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(self.groupBox_config)

        self.remove_enable_checkbox = QCheckBox("Remove Enable Password")
        self.set_new_enable_checkbox = QCheckBox("Set New Enable Password")
        self.encrypt_enable_checkbox = QCheckBox("Use Secret (Encryption)")
        self.new_enable_password_field = PasswordField("New Enable Password")

        self.remove_console_checkbox = QCheckBox("Remove Console Password")
        self.set_new_console_checkbox = QCheckBox("Set New Console Password")
        self.new_console_password_field = PasswordField("New Console Password")

        layout.addWidget(self.remove_enable_checkbox)
        layout.addWidget(self.set_new_enable_checkbox)
        layout.addWidget(self.encrypt_enable_checkbox)
        layout.addWidget(self.new_enable_password_field)
        layout.addSpacing(20)
        layout.addWidget(self.remove_console_checkbox)
        layout.addWidget(self.set_new_console_checkbox)
        layout.addWidget(self.new_console_password_field)
        layout.addSpacing(30)

        self.submit_btn = QPushButton("Start Password Reset")
        self.submit_btn.setMinimumHeight(40)
        layout.addWidget(self.submit_btn)

        layout.addStretch()
        self.middle_layout.addWidget(self.groupBox_config)

    def _connect_ui_constraints(self):
        """
        Connects native QCheckBox toggles to enable/disable specific input dependencies.
        """
        self.set_new_enable_checkbox.toggled.connect(self._on_set_enable_toggled)
        self.set_new_console_checkbox.toggled.connect(self._on_set_console_toggled)
        self.remove_enable_checkbox.toggled.connect(self._on_remove_enable_toggled)
        self.remove_console_checkbox.toggled.connect(self._on_remove_console_toggled)

    def _set_initial_state(self):
        """
        Disables options, terminal, and specific sub-fields on load.
        """
        self.new_enable_password_field.setEnabled(False)
        self.encrypt_enable_checkbox.setEnabled(False)
        self.new_console_password_field.setEnabled(False)
        self._apply_disabled_styles(True)

    def _populate_device_models(self):
        """
        Fetches the hardware list from the central configuration and populates the model selector.
        """
        devices = Devices.get_all()
        model_names = [device.model for device in devices]
        self.device_selector.addItems(model_names)

    def eventFilter(self, source, event):
        """
        Intercepts mouse clicks and focus events on combo boxes to immediately clear validation errors.
        """
        if event.type() in (QEvent.MouseButtonPress, QEvent.FocusIn):
            if source is self.port_input:
                self.clear_error(self.port_input, self.port_error)
            elif source is self.baud_rate_input:
                self.clear_error(self.baud_rate_input, self.baud_error)
            elif source is self.device_selector:
                self.clear_error(self.device_selector, self.device_error)
        return super().eventFilter(source, event)

    def show_field_error(self, field_name: str, message: str):
        """
        Visually highlights connection inputs missing required parameters mimicking BaseInputField.
        """
        if field_name == "port":
            self.port_error.setText(message)
            self.port_error.show()
            self.port_input.setStyleSheet("border: 1px solid red; background-color: rgba(255, 0, 0, 0.1);")
        elif field_name == "baud":
            self.baud_error.setText(message)
            self.baud_error.show()
            self.baud_rate_input.setStyleSheet("border: 1px solid red; background-color: rgba(255, 0, 0, 0.1);")
        elif field_name == "device":
            self.device_error.setText(message)
            self.device_error.show()
            self.device_selector.setStyleSheet("border: 1px solid red; background-color: rgba(255, 0, 0, 0.1);")

    def clear_error(self, field, error_label):
        """
        Removes the validation warning state from a specified input node.
        """
        error_label.hide()
        field.setStyleSheet("")

    def clear_all_errors(self):
        """
        Purges all validation highlight states from the connection interface.
        """
        self.clear_error(self.port_input, self.port_error)
        self.clear_error(self.baud_rate_input, self.baud_error)
        self.clear_error(self.device_selector, self.device_error)

    def _apply_disabled_styles(self, disabled: bool):
        """
        Visually grays out the middle and right sections when no connection is active.
        """
        self.groupBox_config.setEnabled(not disabled)
        self.terminal_view.setEnabled(not disabled)

        if disabled:
            self.submit_btn.setStyleSheet(
                "background-color: #cccccc; color: #666666; font-weight: bold; border-radius: 5px;")
        else:
            self.submit_btn.setStyleSheet(
                "background-color: #28a745; color: white; font-weight: bold; border-radius: 5px;")

    def _on_set_enable_toggled(self, checked: bool):
        """
        Resolves enable constraints when set new enable is modified.
        """
        if checked:
            self.remove_enable_checkbox.setChecked(True)
        self.new_enable_password_field.setEnabled(checked)
        self.encrypt_enable_checkbox.setEnabled(checked)

    def _on_set_console_toggled(self, checked: bool):
        """
        Resolves console constraints when set new console is modified.
        """
        if checked:
            self.remove_console_checkbox.setChecked(True)
        self.new_console_password_field.setEnabled(checked)

    def _on_remove_enable_toggled(self, checked: bool):
        """
        Deselects set new enable when remove enable is deactivated.
        """
        if not checked:
            self.set_new_enable_checkbox.setChecked(False)

    def _on_remove_console_toggled(self, checked: bool):
        """
        Deselects set new console when remove console is deactivated.
        """
        if not checked:
            self.set_new_console_checkbox.setChecked(False)

    def update_connection_state(self, connected: bool):
        """
        Updates the UI to reflect connection status, locking/unlocking areas dynamically.
        """
        if connected:
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: #28a745; font-weight: bold; font-size: 14px;")
            self.connect_button.setText("Disconnect")
            self._apply_disabled_styles(False)
        else:
            self.status_label.setText("Disconnected")
            self.status_label.setStyleSheet("color: #d32f2f; font-weight: bold; font-size: 14px;")
            self.connect_button.setText("Connect")
            self._apply_disabled_styles(True)

    def toggle_input_elements(self, enabled: bool):
        """
        Disables or enables input elements during thread execution states.
        Overrides standard style to ensure submit button grays out during execution.
        """
        self.groupBox_connection.setEnabled(enabled)
        self.groupBox_config.setEnabled(enabled)

        if enabled:
            self.submit_btn.setStyleSheet(
                "background-color: #28a745; color: white; font-weight: bold; border-radius: 5px;")
        else:
            self.submit_btn.setStyleSheet(
                "background-color: #cccccc; color: #666666; font-weight: bold; border-radius: 5px;")

    def get_data(self) -> dict:
        """
        Gathers data from checkboxes and standard fields.
        """
        return {
            "device_model": self.device_selector.currentText(),
            "remove_enable": self.remove_enable_checkbox.isChecked(),
            "set_new_enable": self.set_new_enable_checkbox.isChecked(),
            "encrypt_enable": self.encrypt_enable_checkbox.isChecked(),
            "new_enable_password": self.new_enable_password_field.get_value(),
            "remove_console": self.remove_console_checkbox.isChecked(),
            "set_new_console": self.set_new_console_checkbox.isChecked(),
            "new_console_password": self.new_console_password_field.get_value()
        }