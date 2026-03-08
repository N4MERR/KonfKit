import threading
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox
from utils.cisco_devices import Devices
from model.password_reset_model import PasswordResetModel
from model.port_manager import PortManager


class PasswordResetController(QObject):
    """
    Orchestrates password reset by handling serial connection and delegating execution to the model.
    Operates as a standalone QObject controller independent of BaseConfigController.
    """
    reset_finished = Signal(bool, str)

    def __init__(self, tab_view, session_manager, error_callback):
        """
        Initializes the standalone controller with dependencies.
        Populates static device data immediately on startup.
        """
        super().__init__()
        self.view = tab_view
        self.model = PasswordResetModel()
        self.session_manager = session_manager
        self.show_error = error_callback
        self.port_manager = PortManager()
        self._is_connected = False

        self._setup_signals()
        self._load_initial_data()
        self._bind_terminal()

    def _setup_signals(self):
        """
        Wires UI events to functional logic.
        Only the serial line input is refreshed dynamically.
        """
        self.view.connect_button.clicked.connect(self.toggle_connection)
        self.view.serial_line_input.about_to_show.connect(self.refresh_ports)
        self.view.submit_btn.clicked.connect(self.apply_configuration)
        self.reset_finished.connect(self.on_reset_finished)

    def _bind_terminal(self):
        """
        Connects the active session stream to the local terminal view panel.
        """
        if hasattr(self.session_manager, 'terminal_output_signal'):
            self.session_manager.terminal_output_signal.connect(self.view.terminal_view.append_output)

    def _load_initial_data(self):
        """
        Loads the centralized device list from cisco_devices and populates the UI once at startup.
        """
        device_models = [d.model for d in Devices.get_all()]

        if device_models:
            self.view.device_selector.addItems(device_models)
            self.view.device_selector.setCurrentIndex(-1)

    def refresh_ports(self):
        """
        Dynamically updates the list of available COM ports when the dropdown is clicked.
        Preserves the currently selected text if it remains available.
        """
        current_port = self.view.serial_line_input.currentText()
        ports = [p.device for p in self.port_manager.list_ports()]

        self.view.serial_line_input.clear()
        self.view.serial_line_input.addItems(ports)

        if current_port in ports:
            self.view.serial_line_input.setCurrentText(current_port)

    def toggle_connection(self):
        """
        Manages the NetworkSessionManager serial connection state.
        """
        if self._is_connected:
            self.session_manager.close_connection()
            self._is_connected = False
            self.model.session_manager = None
            self.view.update_connection_state(False)
            return

        port = self.view.serial_line_input.currentText()
        baud_text = self.view.baud_rate_input.currentText()
        device_model = self.view.device_selector.currentText()

        missing = []
        if not port: missing.append("COM Port")
        if not baud_text: missing.append("Baud Rate")
        if not device_model: missing.append("Device Model")

        if missing:
            self.show_error(f"Missing settings: {', '.join(missing)}")
            return

        params = {
            "device_type": "cisco_ios_serial",
            "serial_settings": {"port": port, "baudrate": int(baud_text)}
        }

        success, message = self.session_manager.connect_device(params)
        if success:
            self._is_connected = True
            self.model.session_manager = self.session_manager
            self.view.update_connection_state(True)
        else:
            self.show_error(message)

    def apply_configuration(self):
        """
        Retrieves parameters from the view and triggers the hardware reset thread.
        """
        if not self._is_connected:
            self.show_error("Please connect via Serial first.")
            return

        device_model = self.view.device_selector.currentText()
        device = next((d for d in Devices.get_all() if d.model == device_model), None)

        if not device:
            self.show_error("Invalid device model selected.")
            return

        data = self.view.get_data()

        self.model.remove_privileged_exec_mode_password = data.get("remove_enable", False)
        self.model.remove_line_console_password = data.get("remove_console", False)
        self.model.set_new_privileged_exec_mode_password = data.get("set_new_enable", False)
        self.model.new_privileged_exec_mode_password = data.get("new_enable_password", "")
        self.model.encrypt_enable_password = data.get("encrypt_enable", False)
        self.model.set_new_line_console_password = data.get("set_new_console", False)
        self.model.new_line_console_password = data.get("new_console_password", "")

        self.view.toggle_input_elements(False)
        threading.Thread(target=self._run_reset_thread, args=(device,), daemon=True).start()

    def _run_reset_thread(self, device):
        """
        Executes the hardware reset sequence in a background thread.
        """
        try:
            self.model.reset_password(device)
            self.reset_finished.emit(True, "Password reset completed successfully.")
        except Exception as e:
            self.reset_finished.emit(False, str(e))

    def on_reset_finished(self, success, message):
        """
        Restores the UI state.
        """
        self.view.toggle_input_elements(True)
        if success:
            QMessageBox.information(self.view, "Success", message)
            self._is_connected = False
            self.view.update_connection_state(False)
        else:
            self.show_error(message)