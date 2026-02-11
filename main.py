import sys
import logging
from PySide6.QtWidgets import QApplication
from view.main_window import MainWindow
from controller.main_controller import MainController
from model.connection_manager import ConnectionManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("application.log", mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()

    connection_model = ConnectionManager()

    controller = MainController(window, connection_model)

    window.show()

    sys.exit(app.exec())