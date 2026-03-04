from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QHeaderView, QPushButton, QLineEdit, \
    QSizePolicy
from PySide6.QtCore import Qt


class CellLineEdit(QLineEdit):
    """
    Custom QLineEdit that clears validation styling when it receives focus.
    """

    def focusInEvent(self, event):
        """
        Clears the error stylesheet and tooltip upon focus.
        """
        self.setStyleSheet("border-radius: 0px;")
        self.setToolTip("")
        super().focusInEvent(event)


class ConfigTableWidget(QWidget):
    """
    A dynamic table widget using simple embedded input fields for validation.
    """

    def __init__(self, columns: list, action_buttons: list = None, add_button_text: str = "Add Row"):
        """
        Initializes the table widget with configurable columns and dynamic action buttons.
        """
        super().__init__()
        self.columns = columns
        self.action_buttons = action_buttons if action_buttons is not None else []

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(0, len(columns) + len(self.action_buttons))
        headers = [col.get("header", "") for col in columns] + [""] * len(self.action_buttons)
        self.table.setHorizontalHeaderLabels(headers)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for i in range(len(self.action_buttons)):
            col_idx = len(columns) + i
            self.table.horizontalHeader().setSectionResizeMode(col_idx, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(col_idx, 80)

        self.table.horizontalHeader().setStyleSheet(
            "QHeaderView::section { margin: 0px; padding: 0px; border-radius: 0px; }"
            f"QHeaderView::section:nth-last-child(-n+{len(self.action_buttons)}) {{ border: none; background-color: transparent; color: transparent; }}"
        )

        self.table.setStyleSheet(
            f"QTableWidget::item:nth-last-child(-n+{len(self.action_buttons)}) {{ border: none; background-color: transparent; }}"
            "QTableWidget { border: none; }"
        )

        self.table.horizontalHeader().setSectionsClickable(False)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.verticalHeader().setSectionsClickable(False)
        self.table.verticalHeader().setHighlightSections(False)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setShowGrid(True)

        self.main_layout.addWidget(self.table)

        self.add_btn = QPushButton(add_button_text)
        self.add_btn.setStyleSheet("border-radius: 3px; padding: 5px 15px;")
        self.add_btn.clicked.connect(self._add_empty_row)
        self.main_layout.addWidget(self.add_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def _add_empty_row(self):
        """
        Inserts a new row with basic CellLineEdits and dynamically adds requested action buttons.
        """
        row = self.table.rowCount()
        self.table.insertRow(row)

        for col_idx in range(len(self.columns)):
            edit = CellLineEdit()
            edit.setStyleSheet("border-radius: 0px;")
            self.table.setCellWidget(row, col_idx, edit)

        for btn_idx, btn_data in enumerate(self.action_buttons):
            container = QWidget()
            container.setStyleSheet("background-color: transparent; border: none;")
            layout = QHBoxLayout(container)
            layout.setContentsMargins(4, 2, 4, 2)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn = QPushButton(btn_data.get("text", ""))
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

            color = btn_data.get("color", "#000000")
            btn.setStyleSheet(
                f"QPushButton {{ "
                f"background-color: {color}; "
                f"color: white; "
                f"border-radius: 3px; "
                f"font-weight: bold; "
                f"border: none; "
                f"min-width: 60px; "
                f"min-height: 24px; "
                f"max-height: 24px; "
                f"padding: 0px; "
                f"text-align: center; "
                f"}}"
            )

            callback = btn_data.get("method")
            if callback:
                btn.clicked.connect(lambda checked=False, b=btn, cb=callback: cb(b))

            layout.addWidget(btn)
            self.table.setCellWidget(row, len(self.columns) + btn_idx, container)

    def populate(self, data_list: list):
        """
        Fills the table with a list of dictionaries matching the column keys.
        """
        self.table.setRowCount(0)
        for item in data_list:
            self._add_empty_row()
            row = self.table.rowCount() - 1
            for col_idx, col in enumerate(self.columns):
                key = col["key"]
                edit = self.table.cellWidget(row, col_idx)
                if key in item and isinstance(edit, CellLineEdit):
                    edit.setText(str(item[key]))

    def get_data(self) -> list:
        """
        Extracts data from all rows into a list of dictionaries.
        """
        data = []
        for row in range(self.table.rowCount()):
            row_data = {}
            for col_idx, col in enumerate(self.columns):
                key = col["key"]
                edit = self.table.cellWidget(row, col_idx)
                row_data[key] = edit.text() if isinstance(edit, CellLineEdit) else ""
            data.append(row_data)
        return data

    def _validate_cell(self, edit: CellLineEdit, col_def: dict) -> bool:
        """
        Validates a single cell and updates its border and tooltip.
        """
        text = edit.text()
        required = col_def.get("required", True)
        method = col_def.get("validation_method")
        error_msg = col_def.get("error_message", "Invalid input")

        if not text:
            if required:
                edit.setStyleSheet("border: 1px solid red; border-radius: 0px;")
                edit.setToolTip("Required")
                return False
            else:
                edit.setStyleSheet("border-radius: 0px;")
                edit.setToolTip("")
                return True

        if method and not method(text):
            edit.setStyleSheet("border: 1px solid red; border-radius: 0px;")
            edit.setToolTip(error_msg)
            return False

        edit.setStyleSheet("border-radius: 0px;")
        edit.setToolTip("")
        return True

    def _validate_row(self, row: int) -> bool:
        """
        Validates all cells in a specific row.
        """
        is_valid = True
        for col_idx, col in enumerate(self.columns):
            edit = self.table.cellWidget(row, col_idx)
            if isinstance(edit, CellLineEdit):
                if not self._validate_cell(edit, col):
                    is_valid = False
        return is_valid

    def validate_all(self) -> bool:
        """
        Triggers validation on every cell to ensure the entire table is valid.
        """
        is_valid = True
        for row in range(self.table.rowCount()):
            if not self._validate_row(row):
                is_valid = False
        return is_valid