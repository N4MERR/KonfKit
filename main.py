import sys
import logging
import traceback
from PySide6.QtWidgets import QApplication, QMessageBox
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
    window = MainWindow()

    profile_model = ProfileManager()

    controller = MainController(window, profile_model)

    window.show()
    sys.exit(app.exec())