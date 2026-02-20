from PySide6.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QStackedWidget
from view.password_resetter_tab import PasswordResetTab
from view.connection_dialogs.connection_manager_tab import ConnectionManagerTab
from view.device_config_tab import DeviceConfigTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cisco Management Tool")

        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)

        self.main_tab_widget = QTabWidget()

        self.password_reset_tab = PasswordResetTab()
        self.connection_manager_tab = ConnectionManagerTab()

        self.main_tab_widget.addTab(self.connection_manager_tab, "Connection Manager")
        self.main_tab_widget.addTab(self.password_reset_tab, "Password Resetter")

        self.device_config_tab = DeviceConfigTab()

        self.central_stack.addWidget(self.main_tab_widget)
        self.central_stack.addWidget(self.device_config_tab)

        self.showMaximized()

    def show_error(self, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("System Error")
        msg.setText("An operation failed.")
        msg.setInformativeText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    def show_device_config(self, connection_data):
        self.device_config_tab.set_connection(connection_data)
        self.central_stack.setCurrentWidget(self.device_config_tab)

    def show_home(self):
        self.central_stack.setCurrentWidget(self.main_tab_widget)