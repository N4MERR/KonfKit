from PySide6.QtCore import QObject, QThreadPool
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

        dialog.test_requested.connect(lambda data: self.run_test_process(data, "Testing connection..."))

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
            dialog.name_input.setText(data['name'])
            dialog.ip_input.setText(data['host'])
            dialog.port_input.setText(str(data.get('port', 23)))
            dialog.pass_input.setText(data.get('password', ''))
            dialog.secret_input.setText(data.get('secret', ''))
        elif 'serial' in device_type:
            dialog = SerialConnectionDialog(self.view)
            dialog.name_input.setText(data['name'])
            dialog.port_input.setCurrentText(data['serial_settings']['port'])
            dialog.baud_input.setCurrentText(str(data['serial_settings'].get('baudrate', 9600)))
            dialog.secret_input.setText(data.get('secret', ''))
        else:
            dialog = SSHConnectionDialog(self.view)
            dialog.name_input.setText(data['name'])
            dialog.ip_input.setText(data['host'])
            dialog.port_input.setText(str(data.get('port', 22)))
            dialog.user_input.setText(data.get('username', ''))
            dialog.pass_input.setText(data.get('password', ''))
            dialog.secret_input.setText(data.get('secret', ''))

        dialog.test_requested.connect(lambda test_data: self.run_test_process(test_data, "Testing connection..."))
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
        Shows progress dialog and starts the connection process.
        """
        self.progress_window = ProgressDialog("Connecting to device...", self.view)

        worker = Worker(self._perform_connection_task, data)
        worker.signals.result.connect(self.on_connection_task_finished)
        worker.signals.error.connect(lambda err: self.on_connection_task_finished((False, str(err[1]))))

        self.threadpool.start(worker)
        self.progress_window.exec()

    def _perform_connection_task(self, data):
        """
        Executes a brief validation before passing data to the terminal callback.
        """
        temp_manager = NetworkSessionManager()
        netmiko_settings = {k: v for k, v in data.items() if k != "name"}
        success, msg = temp_manager.connect_device(netmiko_settings)
        if success:
            temp_manager.close_connection()
            return True, data
        return False, msg

    def on_connection_task_finished(self, result):
        """
        Closes progress dialog and transitions to terminal session or shows raw error.
        """
        if self.progress_window:
            self.progress_window.close()
            self.progress_window = None

        success, payload = result
        if success:
            self.start_session(payload)
        else:
            QMessageBox.critical(self.view, "Connection Failed", f"Connection failed: {payload}")

    def run_test_process(self, data, message):
        """
        Starts a background worker to test the network connection.
        """
        self.progress_window = ProgressDialog(message, self.view)

        worker = Worker(self._perform_test, data)
        worker.signals.result.connect(self.on_test_finished)
        worker.signals.error.connect(lambda err: self.on_test_finished((False, str(err[1]))))

        self.threadpool.start(worker)
        self.progress_window.exec()

    def _perform_test(self, data):
        """
        Internal method executed by the worker to attempt a Netmiko connection.
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

    def on_test_finished(self, result):
        """
        Handles the result of the connection test and closes the progress dialog.
        """
        if self.progress_window:
            self.progress_window.close()
            self.progress_window = None

        success, message = result
        if success:
            QMessageBox.information(self.view, "Success", message)
        else:
            QMessageBox.critical(self.view, "Connection Failed", f"Connection failed: {message}")