"""
Main entry point for the application.
Initializes the PySide6 application, sets the theme,
configures error handling, and launches the main window.
"""
import sys
import logging
import traceback
import ctypes
from pathlib import Path
import qdarktheme
from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon
from view.main_window import MainWindow
from controller.main_controller import MainController
from model.connection_profile_manager import ProfileManager


def get_app_dir():
    """
    Determines the directory of the application.
    Ensures accurate paths when compiled to an executable via PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            return Path(sys._MEIPASS)
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


APP_DIR = get_app_dir()

error_handler = logging.FileHandler(APP_DIR / "error.log", mode='a', encoding='utf-8')
error_handler.setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[error_handler]
)


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Global exception handler to catch unhandled exceptions, log them,
    and display a structured GUI error message.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    app = QApplication.instance()
    if app:
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText("A critical unexpected error occurred. Please check the details and logs.")
        msg_box.setDetailedText(error_msg)
        msg_box.exec()


sys.excepthook = handle_exception

if __name__ == "__main__":
    if sys.platform == "win32":
        myappid = "konfkit.main.application.2"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)

    app_icon = QIcon()
    app_icon.addFile(str(APP_DIR / 'resources' / 'logo_128x128.ico'))
    app.setWindowIcon(app_icon)

    qdarktheme.setup_theme("dark")

    window = MainWindow()
    profile_model = ProfileManager(filename=str(APP_DIR / "connections.json"))
    controller = MainController(window, profile_model)
    window.show()

    sys.exit(app.exec())