from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox
from PySide6.QtCore import Signal


class BaseTableConfigView(QWidget):
    """
    Base view for table-based device configuration tabs allowing individual row configuration application.
    """
    load_config_signal = Signal()
    apply_row_signal = Signal(str, dict)

    def __init__(self):
        """
        Initializes the base table configuration view layout with a load button and write memory toggle.
        """
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

        self.setStyleSheet(
            "QLabel { background: transparent; }"
            "QCheckBox { background: transparent; }"
        )

        self.form_layout = QVBoxLayout()
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setSpacing(15)

        self.main_layout.addLayout(self.form_layout)

        self.button_layout = QHBoxLayout()

        self.write_memory_cb = QCheckBox("Write Memory")
        self.load_button = QPushButton("Load Current Config")

        self.button_layout.addWidget(self.load_button)
        self.button_layout.addWidget(self.write_memory_cb)
        self.button_layout.addStretch()

        self.form_layout.addStretch(1)
        self.main_layout.addLayout(self.button_layout)

        self.load_button.clicked.connect(self._on_load_clicked)

    def populate_data(self, data: dict):
        """
        Populates the tables with data loaded from the device.
        Must be implemented by subclasses.
        """
        raise NotImplementedError

    def _on_load_clicked(self):
        """
        Emits signal to load configuration from the device into the tables.
        """
        self.load_config_signal.emit()