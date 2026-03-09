import threading
import logging
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox
from utils.cisco_devices import Devices
from model.password_reset_model import PasswordResetModel
from model.raw_serial_session_manager import RawSerialSessionManager

logger = logging.getLogger(__name__)


class PasswordResetController(QObject):
    """
    Orchestrates password reset by handling raw serial connection and delegating execution to the model.
    Operates independently of the global Netmiko session manager to accommodate bootloader states.
    """
    reset_finished = Signal(bool, str)

    def __init__(self, tab_view, session_manager, error_callback):
        """
        Initializes the controller with an isolated raw serial manager explicitly for hardware recovery.
        """
        super().__init__()
        self.view = tab_view
        self.model = PasswordResetModel()
        self.raw_session_manager = RawSerialSessionManager()
        self.show_error = error_callback
        self._is_connected = False

        self._setup_signals()
        self._load_initial_data()
        self._bind_terminal()

    def _setup_signals(self):
        """
        Wires UI events to functional logic.
        """
        self.view.connect_button.clicked.connect(self.toggle_connection)
        self.view.submit_btn.clicked.connect(self.apply_configuration)
        self.reset_finished.connect(self.on_reset_finished)
        self.raw_session_manager.connection_lost.connect(self._handle_disconnection)
        self.raw_session_manager.error_occurred.connect(self._display_error)

    def _bind_terminal(self):
        """
        Connects the raw serial stream directly to the local terminal view panel.
        """
        self.raw_session_manager.data_received.connect(self._append_to_terminal)

    def _append_to_terminal(self, text: str):
        """
        Dynamically routes received text to the terminal view regardless of the underlying widget implementation.
        """
        if hasattr(self.view.terminal_view, 'append_text'):
            self.view.terminal_view.append_text(text)
        elif hasattr(self.view.terminal_view, 'appendPlainText'):
            self.view.terminal_view.appendPlainText(text)
        elif hasattr(self.view.terminal_view, 'append'):
            self.view.terminal_view.append(text)
        elif hasattr(self.view.terminal_view, 'insertPlainText'):
            self.view.terminal_view.insertPlainText(text)
        elif hasattr(self.view.terminal_view, 'update_terminal'):
            self.view.terminal_view.update_terminal(text)
        elif hasattr(self.view.terminal_view, 'write'):
            self.view.terminal_view.write(text)

    def _load_initial_data(self):
        """
        Loads the centralized device list from cisco_devices and populates the UI once at startup.
        """
        device_models = [d.model for d in Devices.get_all()]

        if device_models:
            self.view.device_selector.clear()
            self.view.device_selector.addItems(device_models)
            self.view.device_selector.setCurrentIndex(-1)

    def _display_error(self, message: str):
        """
        Forces a UI popup for errors instead of relying on a potentially silent background callback.
        """
        logger.error(f"Displaying error to user: {message}")
        QMessageBox.critical(self.view, "Connection Error", message)
        self.show_error(message)

    def toggle_connection(self):
        """
        Manages the raw serial connection state for hardware recovery operations.
        Logs every step to trace silent failures.
        """
        logger.info("Connect button clicked!")

        if self._is_connected:
            logger.info("State is currently connected. Disconnecting...")
            self.raw_session_manager.close_connection()
            self._is_connected = False
            self.model.session_manager = None
            self.view.update_connection_state(False)
            return

        logger.info("Attempting to initialize connection...")

        port_text = self.view.port_input.currentText() if hasattr(self.view.port_input, "currentText") else getattr(
            self.view.port_input, "get_value", lambda: "")()
        baud_text = self.view.baud_rate_input.currentText()
        device_model = self.view.device_selector.currentText()

        logger.info(f"Retrieved connection values - Port: '{port_text}', Baud: '{baud_text}', Model: '{device_model}'")

        missing = []
        if not port_text: missing.append("COM Port")
        if not baud_text: missing.append("Baud Rate")
        if not device_model: missing.append("Device Model")

        if missing:
            error_msg = f"Missing settings: {', '.join(missing)}"
            logger.warning(f"Validation failed. {error_msg}")
            self._display_error(error_msg)
            return

        logger.info(f"Initiating raw serial connection to {port_text} at {baud_text} baud...")
        success, message = self.raw_session_manager.connect_device(port_text, int(baud_text))

        if success:
            logger.info("Connection established successfully.")
            self._is_connected = True
            self.model.session_manager = self.raw_session_manager
            self.view.update_connection_state(True)
        else:
            logger.error(f"Connection failed to establish: {message}")
            self._display_error(message)

    def apply_configuration(self):
        """
        Retrieves parameters from the view and triggers the hardware reset sequence in a background thread.
        """
        if not self._is_connected:
            self._display_error("Please connect via Serial first.")
            return

        device_model = self.view.device_selector.currentText()
        device = next((d for d in Devices.get_all() if d.model == device_model), None)

        if not device:
            self._display_error("Invalid device model selected.")
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
        self.raw_session_manager.clear_buffer()
        threading.Thread(target=self._run_reset_thread, args=(device,), daemon=True).start()

    def _run_reset_thread(self, device):
        """
        Executes the hardware reset sequence utilizing the robust pattern matching of the raw session.
        """
        try:
            self.model.reset_password(device)
            self.reset_finished.emit(True, "Password reset completed successfully. The device is now reloading.")
        except Exception as e:
            self.reset_finished.emit(False, str(e))

    def _handle_disconnection(self, message):
        """
        Resets the connection state when the raw serial line drops or is closed.
        """
        self._is_connected = False
        self.model.session_manager = None
        self.view.update_connection_state(False)

    def on_reset_finished(self, success, message):
        """
        Restores the UI state following the execution of the background sequence.
        """
        self.view.toggle_input_elements(True)
        if success:
            QMessageBox.information(self.view, "Success", message)
            self._is_connected = False
            self.view.update_connection_state(False)
        else:
            self._display_error(message)