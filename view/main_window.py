from PySide6.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QStackedWidget, QApplication
from view.connection_dialogs.connection_manager_tab import ConnectionManagerTab
from view.config_tab.device_config_tab import DeviceConfigTab
from view.password_reset_view import PasswordResetView
from view.progress_dialog import ProgressDialog


class MainWindow(QMainWindow):
    """
    Main application window containing the tabbed interface adapting to the system theme.
    """

    def __init__(self):
        """
        Initializes the main window and its UI components.
        """
        super().__init__()
        self.setWindowTitle("Cisco Management Tool")

        self.progress = None

        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)

        self.main_tab_widget = QTabWidget()

        self.main_tab_widget.setStyleSheet("""
            QTabWidget::pane { 
                border: 1px solid rgba(128, 128, 128, 0.2); 
                border-radius: 4px; 
                background: transparent; 
            }
            QTabBar::tab {
                height: 30px;
                width: 155px;
                font-size: 10pt;
                font-weight: bold;
                margin-top: 2px;
                margin-right: 1px;
                margin-left: 1px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid rgba(128, 128, 128, 0.3);
            }
            QTabBar::tab:selected {
                background-color: rgba(0, 120, 212, 0.1);
                border: 1px solid #0078d4;
                border-bottom: none;
            }
            QTabBar::tab:hover:!selected {
                background-color: rgba(0, 120, 212, 0.05);
            }
        """)

        self.password_reset_tab = PasswordResetView()
        self.connection_manager_tab = ConnectionManagerTab()

        self.main_tab_widget.addTab(self.connection_manager_tab, "Connection Manager")
        self.main_tab_widget.addTab(self.password_reset_tab, "Password Resetter")

        self.device_config_tab = DeviceConfigTab()

        self.central_stack.addWidget(self.main_tab_widget)
        self.central_stack.addWidget(self.device_config_tab)

        self.showMaximized()

    def show_error(self, message):
        """
        Displays a critical error message box.
        """
        QMessageBox.critical(self, "System Error", f"An operation failed.\n\n{message}")

    def ask_question(self, title, message):
        """
        Displays a question dialog and returns True if the user confirms.
        """
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def show_progress(self, message):
        """
        Displays a non-blocking progress dialog and forces UI update.
        """
        self.progress = ProgressDialog(message, self)
        self.progress.show()
        QApplication.processEvents()

    def hide_progress(self):
        """
        Closes and clears the active progress dialog.
        """
        if self.progress:
            self.progress.close()
            self.progress = None

    def show_device_config(self, connection_data):
        """
        Switches the view to the device configuration tab.
        """
        self.device_config_tab.set_connection(connection_data)
        self.central_stack.setCurrentWidget(self.device_config_tab)

    def show_home(self):
        """
        Switches the view back to the main tab widget.
        """
        self.central_stack.setCurrentWidget(self.main_tab_widget)