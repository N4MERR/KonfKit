"""
Main application entry point.
Initializes logging, global exception handling, and the PySide6 application with a forced native dark mode color scheme.
"""
import sys
import logging
import traceback
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from view.main_window import MainWindow
from controller.main_controller import MainController
from model.connection_profile_manager import ProfileManager

app_handler = logging.FileHandler("application.log", mode='a', encoding='utf-8')
app_handler.setLevel(logging.INFO)

error_handler = logging.FileHandler("error.log", mode='a', encoding='utf-8')
error_handler.setLevel(logging.ERROR)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[app_handler, error_handler, stream_handler]
)


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Global exception handler to catch unhandled exceptions, log them,
    and display a structured GUI error message to the user.
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
        msg_box.setWindowTitle("Critical Error")
        msg_box.setText("An unexpected error occurred.")
        msg_box.setDetailedText(error_msg)
        msg_box.exec()


sys.excepthook = handle_exception

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.styleHints().setColorScheme(Qt.ColorScheme.Dark)

    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(dark_palette)

    app.setStyleSheet(
        "QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }"
    )

    window = MainWindow()

    profile_model = ProfileManager()

    controller = MainController(window, profile_model)

    window.show()
    sys.exit(app.exec())