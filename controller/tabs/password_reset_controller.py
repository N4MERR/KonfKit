import logging
import threading
from PySide6.QtCore import QObject, Signal
from utils.exceptions import CiscoToolError
from model.password_resetter import PasswordResetter
from model.port_manager import PortManager

logger = logging.getLogger(__name__)

class PasswordResetController(QObject):
    """
    Controller for the Password Reset tab managing connection logic and reset execution.
    """
    reset_finished = Signal(bool, str)

    def __init__(self, tab_view, serial_manager, error_callback):
        super().__init__()
        self.view = tab_view
        self.serial_manager = serial_manager
        self.show_error = error_callback
        self.resetter = PasswordResetter()
        self.port_manager = PortManager()
        self._is_connected = False
        self._connect_signals()
        self._init_data()

    def _connect_signals(self):
        self.view.get_connect_button().clicked.connect(self.handle_connection_toggle)
        self.view.get_confirm_button().clicked.connect(self.handle_reset_request)
        self.view.get_refresh_button().clicked.connect(self.refresh_ports)
        self.reset_finished.connect(self.on_reset_finished)

    def _init_data(self):
        self.refresh_ports()
        from utils.cisco_devices import Devices
        device_models = [d.model for d in Devices.get_all()]
        self.view.set_device_list(device_models)
        self.view.set_baud_rate_list(["9600", "19200", "38400", "57600", "115200"])

    def refresh_ports(self):
        ports = [p.device for p in self.port_manager.list_ports()]
        self.view.set_port_list(ports)

    def handle_connection_toggle(self):
        if self._is_connected:
            self.serial_manager.close_connection()
            self._is_connected = False
            self.view.update_status_led(False)
            return

        missing = []
        if not self.view.get_port(): missing.append("COM Port")
        if not self.view.get_baud_rate(): missing.append("Baud Rate")
        if not self.view.get_selected_device(): missing.append("Device Model")

        if missing:
            self.show_error(f"Missing settings: {', '.join(missing)}")
            return

        try:
            self.serial_manager.port = self.view.get_port()
            self.serial_manager.baud_rate = self.view.get_baud_rate()
            self.serial_manager.open_serial_connection()
            self._is_connected = True
            self.view.update_status_led(True)
        except Exception as e:
            self.show_error(f"Failed to connect: {str(e)}")

    def handle_reset_request(self):
        try:
            if not self._is_connected:
                raise CiscoToolError("Please connect to a device first.")

            device_model = self.view.get_selected_device()
            from utils.cisco_devices import Devices
            device = next((d for d in Devices.get_all() if d.model == device_model), None)

            if not device:
                raise CiscoToolError("Invalid device model selected.")

            self.resetter.remove_privileged_exec_mode_password = self.view.is_remove_enable_checked()
            self.resetter.remove_line_console_password = self.view.is_remove_console_checked()
            self.resetter.set_new_privileged_exec_mode_password = self.view.is_set_new_enable_checked()
            self.resetter.new_privileged_exec_mode_password = self.view.get_new_enable_pass()
            self.resetter.encrypt_enable_password = self.view.is_encrypt_enable_checked()
            self.resetter.set_new_line_console_password = self.view.is_set_new_console_checked()
            self.resetter.new_line_console_password = self.view.get_new_console_pass()

            self.view.set_ui_locked(True)
            threading.Thread(target=self._run_reset_thread, args=(device,), daemon=True).start()

        except CiscoToolError as e:
            self.show_error(str(e))
            self.view.set_ui_locked(False)
        except Exception as e:
            logger.critical(f"System Error: {e}", exc_info=True)
            self.show_error("An unexpected internal application error occurred.")
            self.view.set_ui_locked(False)

    def _run_reset_thread(self, device):
        try:
            self.resetter.reset_password(self.serial_manager, device)
            self.reset_finished.emit(True, "Password reset completed successfully.")
        except CiscoToolError as e:
            self.reset_finished.emit(False, str(e))
        except Exception as e:
            logger.error(f"Thread error: {e}", exc_info=True)
            self.reset_finished.emit(False, "A hardware communication error occurred.")

    def on_reset_finished(self, success, message):
        self.view.set_ui_locked(False)
        if success:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self.view, "Success", message)
        else:
            self.show_error(message)