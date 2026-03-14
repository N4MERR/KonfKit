from PySide6.QtCore import QObject, QThreadPool, QTimer
from PySide6.QtWidgets import QMessageBox
from model.worker import Worker
from view.connection_dialogs.serial_connection_dialog import SerialConnectionDialog
from view.connection_dialogs.ssh_connection_dialog import SSHConnectionDialog
from view.connection_dialogs.telnet_connection_dialog import TelnetConnectionDialog
from view.progress_dialog import ProgressDialog
from model.network_session_manager import NetworkSessionManager


class ConnectionProfileController(QObject):
    """
    Controller managing connection profiles and testing connectivity via NetworkSessionManager.
    """

    def __init__(self, view, model, terminal_callback):
        """
        Initializes the controller with view, model, and the callback to start a terminal session.
        """
        super().__init__()
        self.view = view
        self.model = model
        self.start_session = terminal_callback
        self.threadpool = QThreadPool.globalInstance()
        self.progress_window = None
        self._connect_signals()
        self.refresh_ui()

    def _connect_signals(self):
        """
        Connects UI signals from the ConnectionManagerTab to handler methods.
        """
        self.view.serial_row.add_requested.connect(lambda: self.handle_add_with_protocol("Serial"))
        self.view.ssh_row.add_requested.connect(lambda: self.handle_add_with_protocol("SSH"))
        self.view.telnet_row.add_requested.connect(lambda: self.handle_add_with_protocol("Telnet"))

        self.view.connect_profile_requested.connect(self.handle_connect_profile)
        self.view.edit_profile_requested.connect(self.handle_edit_profile)
        self.view.delete_profile_requested.connect(self.handle_delete_profile)

    def refresh_ui(self):
        """
        Updates the view with the latest profile list from the model.
        """
        self.view.update_list(self.model.get_profiles())

    def handle_add_with_protocol(self, protocol):
        """
        Opens the appropriate connection dialog based on the selected protocol.
        """
        if protocol == "SSH":
            dialog = SSHConnectionDialog(self.view)
        elif protocol == "Telnet":
            dialog = TelnetConnectionDialog(self.view)
        elif protocol == "Serial":
            dialog = SerialConnectionDialog(self.view)
        else:
            return

        dialog.test_requested.connect(lambda data, d=dialog: self.run_test_process(data, "Testing connection...", d))

        result = dialog.exec()
        if result == 10:
            data = dialog.get_data()
            self.model.save_profile(data)
            self.refresh_ui()
        elif result == 20:
            data = dialog.get_data()
            self.handle_connect_profile(data)

    def handle_edit_profile(self, data):
        """
        Populates a dialog with existing profile data for editing.
        """
        device_type = data.get('device_type', '')
        if 'telnet' in device_type:
            dialog = TelnetConnectionDialog(self.view)
            dialog.name_input.input_widget.setText(data['name'])
            dialog.ip_input.input_widget.setText(data['host'])
            dialog.port_input.input_widget.setText(str(data.get('port', 23)))

            if data.get('username'):
                dialog.auth_mode.input_widget.setCurrentText("Login Local")
            elif data.get('password'):
                dialog.auth_mode.input_widget.setCurrentText("Login")
            else:
                dialog.auth_mode.input_widget.setCurrentText("No Login")

            dialog.user_input.input_widget.setText(data.get('username', ''))
            dialog.pass_input.input_widget.setText(data.get('password', ''))
            dialog.enable_pass_input.input_widget.setText(data.get('secret', ''))

        elif 'serial' in device_type:
            dialog = SerialConnectionDialog(self.view)
            dialog.name_input.input_widget.setText(data['name'])
            dialog.port_input.input_widget.setCurrentText(data['serial_settings']['port'])
            dialog.baud_input.input_widget.setCurrentText(str(data['serial_settings'].get('baudrate', 9600)))

            if data.get('username'):
                dialog.auth_mode.input_widget.setCurrentText("Login Local")
            elif data.get('password'):
                dialog.auth_mode.input_widget.setCurrentText("Login")
            else:
                dialog.auth_mode.input_widget.setCurrentText("No Login")

            dialog.user_input.input_widget.setText(data.get('username', ''))
            dialog.pass_input.input_widget.setText(data.get('password', ''))

            if data.get('secret'):
                dialog.enable_pass_input.radio.setChecked(True)
                dialog.enable_pass_input.input_widget.setText(data.get('secret'))
            else:
                dialog.enable_pass_input.radio.setChecked(False)

        else:
            dialog = SSHConnectionDialog(self.view)
            dialog.name_input.input_widget.setText(data['name'])
            dialog.ip_input.input_widget.setText(data['host'])
            dialog.port_input.input_widget.setText(str(data.get('port', 22)))
            dialog.user_input.input_widget.setText(data.get('username', ''))
            dialog.pass_input.input_widget.setText(data.get('password', ''))
            dialog.enable_pass_input.input_widget.setText(data.get('secret', ''))

        dialog.test_requested.connect(lambda test_data, d=dialog: self.run_test_process(test_data, "Testing connection...", d))
        result = dialog.exec()

        if result == 10:
            new_data = dialog.get_data()
            self.model.save_profile(new_data)
            self.refresh_ui()
        elif result == 20:
            self.handle_connect_profile(dialog.get_data())

    def handle_delete_profile(self, data):
        """
        Prompts for confirmation before deleting a profile.
        """
        reply = QMessageBox.question(self.view, "Delete Profile",
                                     f"Are you sure you want to delete profile '{data['name']}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.model.delete_profile(data['name'], data['device_type'])
            self.refresh_ui()

    def handle_connect_profile(self, data):
        """
        Passes the connection data to the main controller to establish the session directly.
        """
        self.start_session(data)

    def run_test_process(self, data, message, parent_widget=None):
        """
        Starts a background worker to test the network connection for the dialogs.
        """
        parent = parent_widget if parent_widget else self.view
        self.progress_window = ProgressDialog(message, parent)

        worker = Worker(self._perform_test, data)
        worker.signals.result.connect(lambda res: self.on_test_finished(res, parent))
        worker.signals.error.connect(lambda err: self.on_test_finished((False, str(err[1])), parent))

        self.threadpool.start(worker)
        self.progress_window.exec()

    def _perform_test(self, data):
        """
        Internal method executed by the worker to attempt a Netmiko connection test.
        """
        temp_manager = NetworkSessionManager()
        netmiko_settings = {k: v for k, v in data.items() if k != "name"}

        try:
            success, msg = temp_manager.connect_device(netmiko_settings)
            if success:
                temp_manager.close_connection()
                return True, "Successfully reached device."
            return False, msg
        except Exception as e:
            return False, str(e)

    def on_test_finished(self, result, parent_widget):
        """
        Handles the result of the connection test and closes the progress dialog.
        Schedules the result message box to allow UI focus to settle on the parent dialog.
        """
        if self.progress_window:
            self.progress_window.close()
            self.progress_window = None

        QTimer.singleShot(100, lambda: self._show_test_result(result, parent_widget))

    def _show_test_result(self, result, parent_widget):
        """
        Displays the success or failure message box for the connection test.
        """
        success, message = result
        if success:
            QMessageBox.information(parent_widget, "Success", message)
        else:
            QMessageBox.critical(parent_widget, "Connection Failed", f"Connection failed: {message}")