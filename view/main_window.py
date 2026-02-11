from PySide6.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from view.password_resetter_tab import PasswordResetTab
from view.connection_manager.connection_manager_tab import ConnectionManagerTab


class MainWindow(QMainWindow):
    """
    Main application window hosting the Connection Manager and Password Resetter.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cisco Management Tool")

        self.main_tab_widget = QTabWidget()
        self.setCentralWidget(self.main_tab_widget)

        self.password_reset_tab = PasswordResetTab()
        self.connection_manager_tab = ConnectionManagerTab()

        self.main_tab_widget.addTab(self.connection_manager_tab, "Connection Manager")
        self.main_tab_widget.addTab(self.password_reset_tab, "Password Resetter")

        self.showMaximized()

    def show_error(self, message):
        """
        Displays a standardized error dialog for hardware or network failures.
        """
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("System Error")
        msg.setText("An operation failed.")
        msg.setInformativeText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()