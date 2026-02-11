from PySide6.QtCore import QObject, QThreadPool, Qt
from PySide6.QtWidgets import QMessageBox
from model.worker import Worker
from view.connection_manager.serial_connection_dialog import SerialConnectionDialog
from view.connection_manager.ssh_connection_dialog import SSHConnectionDialog
from view.connection_manager.telnet_connection_dialog import TelnetConnectionDialog

class ConnectionController(QObject):
    """
    Controller managing connection profiles and executing protocol-specific background connectivity tests.
    """
    def __init__(self, view, model, terminal_callback):
        super().__init__()
        self.view = view
        self.model = model
        self.start_session = terminal_callback
        self.threadpool = QThreadPool.globalInstance()
        self._connect_signals()
        self.refresh_ui()

    def _connect_signals(self):
        """
        Connects main view triggers to protocol handlers.
        """
        self.view.serial_row.add_requested.connect(lambda: self.handle_add_with_protocol("Serial"))
        self.view.ssh_row.add_requested.connect(lambda: self.handle_add_with_protocol("SSH"))
        self.view.telnet_row.add_requested.connect(lambda: self.handle_add_with_protocol("Telnet"))

    def refresh_ui(self):
        """
        Updates the UI with current connection profiles.
        """
        self.view.update_list(self.model.connections)

    def handle_add_with_protocol(self, protocol):
        """
        Launches connection dialogs and handles direct connection vs saving.
        """
        if protocol == "SSH":
            dialog = SSHConnectionDialog(self.view)
            dialog.test_requested.connect(lambda data: self.run_protocol_test(data, dialog, "SSH"))
        elif protocol == "Telnet":
            dialog = TelnetConnectionDialog(self.view)
            dialog.test_requested.connect(lambda data: self.run_protocol_test(data, dialog, "Telnet"))
        elif protocol == "Serial":
            dialog = SerialConnectionDialog(self.view)
            dialog.test_requested.connect(lambda data: self.run_protocol_test(data, dialog, "Serial"))
        else:
            return

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

    def run_protocol_test(self, data, dialog, protocol):
        """
        Initializes background testing via Worker using the specific library method for the protocol.
        """
        dialog.set_loading(True)
        if protocol == "SSH":
            worker = Worker(
                self.model.test_ssh,
                data['host'],
                data['port'],
                5.0,
                data.get('username', ''),
                data.get('password', '')
            )
        elif protocol == "Telnet":
            worker = Worker(
                self.model.test_telnet,
                data['host'],
                data['port'],
                5.0,
                data.get('username', ''),
                data.get('password', '')
            )
        else:
            worker = Worker(self.model.test_serial_connection, data['host'], data['baud'])

        worker.signals.result.connect(lambda res: self.on_test_finished(res, dialog))
        worker.signals.error.connect(lambda err: self.on_test_finished((False, str(err[1])), dialog))
        self.threadpool.start(worker)

    def on_test_finished(self, result, dialog):
        """
        Updates dialog state and alerts user of test results.
        """
        success, message = result
        dialog.set_loading(False)
        if success:
            QMessageBox.information(dialog, "Test Success", message)
        else:
            QMessageBox.critical(dialog, "Test Failed", f"Connection failed: {message}")