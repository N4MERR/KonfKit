from PySide6.QtCore import QObject, QThreadPool, Qt
from PySide6.QtWidgets import QMessageBox
from model.worker import Worker
from view.connection_manager.serial_connection_dialog import SerialConnectionDialog
from view.connection_manager.ssh_connection_dialog import SSHConnectionDialog
from view.connection_manager.telnet_connection_dialog import TelnetConnectionDialog
from view.progress_dialog import ProgressDialog

class ConnectionController(QObject):
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
        self.view.serial_row.add_requested.connect(lambda: self.handle_add_with_protocol("Serial"))
        self.view.ssh_row.add_requested.connect(lambda: self.handle_add_with_protocol("SSH"))
        self.view.telnet_row.add_requested.connect(lambda: self.handle_add_with_protocol("Telnet"))

        self.view.connect_profile_requested.connect(self.start_session)
        self.view.edit_profile_requested.connect(self.handle_edit_profile)
        self.view.delete_profile_requested.connect(self.handle_delete_profile)

    def refresh_ui(self):
        self.view.update_list(self.model.connections)

    def handle_add_with_protocol(self, protocol):
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
            success, message = self.model.save_connection(
                data['name'], data['host'], data.get('username', ''),
                data.get('password', ''), data['protocol'],
                baud=data.get('baud'), port=data.get('port')
            )
            if not success:
                QMessageBox.warning(self.view, "Duplicate Name", message)
                return
            self.refresh_ui()
        elif result == 20:
            data = dialog.get_data()
            self.start_session(data)

    def handle_edit_profile(self, data):
        if data['protocol'] == "SSH":
            dialog = SSHConnectionDialog(self.view)
            dialog.name_input.setText(data['name'])
            dialog.ip_input.setText(data['host'])
            dialog.port_input.setText(str(data.get('port', 22)))
            dialog.user_input.setText(data.get('username', ''))
            dialog.pass_input.setText(data.get('password', ''))
        elif data['protocol'] == "Telnet":
            dialog = TelnetConnectionDialog(self.view)
            dialog.name_input.setText(data['name'])
            dialog.ip_input.setText(data['host'])
            dialog.port_input.setText(str(data.get('port', 23)))
            dialog.pass_input.setText(data.get('password', ''))
        elif data['protocol'] == "Serial":
            dialog = SerialConnectionDialog(self.view)
            dialog.name_input.setText(data['name'])
            dialog.port_input.setCurrentText(data['host'])
            dialog.baud_input.setCurrentText(str(data.get('baud', 9600)))
        else:
            return

        dialog.test_requested.connect(lambda test_data: self.run_test_process(test_data, "Testing connection..."))
        result = dialog.exec()

        if result == 10:
            new_data = dialog.get_data()
            self.update_profile_in_model(data, new_data)
        elif result == 20:
            self.start_session(dialog.get_data())

    def update_profile_in_model(self, old_data, new_data):
        for i, c in enumerate(self.model.connections):
            if c['name'] == old_data['name'] and c['protocol'] == old_data['protocol']:
                self.model.connections[i] = new_data
                break
        self.model._write_to_file()
        self.refresh_ui()

    def handle_delete_profile(self, data):
        reply = QMessageBox.question(self.view, "Delete Profile",
                                     f"Are you sure you want to delete profile '{data['name']}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.model.connections = [c for c in self.model.connections if
                                      not (c['name'] == data['name'] and c['protocol'] == data['protocol'])]
            self.model._write_to_file()
            self.refresh_ui()

    def run_test_process(self, data, message):
        self.progress_window = ProgressDialog(message, self.view)

        if data['protocol'] == "SSH":
            worker = Worker(self.model.test_ssh, data['host'], data['port'], 5.0,
                            data.get('username', ''), data.get('password', ''))
        elif data['protocol'] == "Telnet":
            worker = Worker(self.model.test_telnet, data['host'], data['port'], 5.0,
                            data.get('password', ''))
        else:
            worker = Worker(self.model.test_serial_connection, data['host'], data['baud'])

        worker.signals.result.connect(self.on_test_finished)
        worker.signals.error.connect(lambda err: self.on_test_finished((False, str(err[1]))))

        self.threadpool.start(worker)
        self.progress_window.exec()

    def on_test_finished(self, result):
        if self.progress_window:
            self.progress_window.close()
            self.progress_window = None

        success, message = result
        if success:
            QMessageBox.information(self.view, "Success", message)
        else:
            QMessageBox.critical(self.view, "Failed", f"Process failed: {message}")