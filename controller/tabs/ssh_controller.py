from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QMessageBox
from model.ssh_connection_manager import SSHConnectionManager
import threading
import paramiko


class SSHController(QObject):
    test_finished = Signal(bool, str)

    def __init__(self, view, error_callback):
        super().__init__()
        self.view = view
        self.show_error = error_callback
        self.model = SSHConnectionManager()
        self._active_dialog = None

        self.test_finished.connect(self.on_test_result)
        self._refresh_view()
        self._connect_signals()

    def _connect_signals(self):
        self.view.add_requested.connect(self.open_add_dialog)
        self.view.card_action.connect(self.handle_card_action)
        self.model.connections_updated.connect(self._refresh_view)

    def _refresh_view(self):
        self.view.update_list(self.model.connections)

    def open_add_dialog(self):
        dialog = SSHEditDialog(self.view)
        dialog.test_btn.clicked.connect(lambda: self.run_threaded_test(dialog))
        if dialog.exec():
            data = dialog.get_data()
            self.model.save_connection(data['name'], data['host'], data['username'], data['password'])

    def run_threaded_test(self, dialog):
        """Validates inputs before initiating the threaded SSH test."""
        data = dialog.get_data()
        errors = []

        if not data['host']:
            errors.append("- IP Address is required for testing.")
        elif not dialog.host_input.hasAcceptableInput():
            errors.append("- IP Address format is invalid.")
        if not data['username']:
            errors.append("- Username is required for testing.")
        if not data['password']:
            errors.append("- Password is required for testing.")

        if errors:
            QMessageBox.warning(
                dialog,
                "Test Failed",
                "Incomplete credentials:\n\n" + "\n".join(errors)
            )
            return

        dialog.test_btn.setEnabled(False)
        dialog.test_btn.setText("Connecting...")
        self._active_dialog = dialog

        thread = threading.Thread(target=self._ssh_test_worker, args=(data,), daemon=True)
        thread.start()

    def _show_validation_error(self, parent, title, message):
        """Custom styled error window for incorrect input."""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox { background-color: #2b2b2b; }
            QLabel { color: white; font-weight: bold; }
            QPushButton { background-color: #444; color: white; width: 80px; height: 25px; }
        """)
        msg.exec()

    def _ssh_test_worker(self, data):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=data['host'], username=data['username'],
                           password=data['password'], timeout=5)
            client.close()
            self.test_finished.emit(True, "SSH Connection Successful!")
        except Exception as e:
            self.test_finished.emit(False, str(e))

    def on_test_result(self, success, message):
        if self._active_dialog:
            self._active_dialog.test_btn.setEnabled(True)
            self._active_dialog.test_btn.setText("Test Connection")
            if success:
                QMessageBox.information(self._active_dialog, "Success", message)
            else:
                self.show_error(f"SSH Test Failed: {message}")

    def handle_card_action(self, action_type, index):
        if action_type == "delete":
            self.model.delete_connection(index)
        elif action_type == "edit":
            self.open_edit_dialog(index)

    def open_edit_dialog(self, index):
        conn_data = self.model.connections[index]
        dialog = SSHEditDialog(self.view, conn_data)
        dialog.test_btn.clicked.connect(lambda: self.run_threaded_test(dialog))
        if dialog.exec():
            self.model.connections[index] = dialog.get_data()
            self.model._write_to_file()
            self.model.connections_updated.emit()