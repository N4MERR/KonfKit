from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Signal
from view.device_configuration_views.base_table_config_view import BaseTableConfigView
from view.device_configuration_views.config_table_widget import ConfigTableWidget
from utils.input_validator import InputValidator

class DHCPView(BaseTableConfigView):
    """
    View for managing DHCP with explicit signals for different configuration actions.
    """

    apply_pool_signal = Signal(dict)
    delete_pool_signal = Signal(dict)
    apply_exclusion_signal = Signal(dict)
    delete_exclusion_signal = Signal(dict)

    def __init__(self):
        """
        Initializes the view and setups the DHCP tables.
        """
        super().__init__()
        self.form_layout.insertWidget(0, QLabel("<b>DHCP Pools:</b>"))

        pool_buttons = [
            {"text": "Apply", "color": "#2e7d32", "method": self._on_apply_pool},
            {"text": "Delete", "color": "#d32f2f", "method": self._on_delete_pool}
        ]

        self.pool_table = ConfigTableWidget(
            columns=[
                {"header": "Pool Name", "key": "name", "validation_method": InputValidator.is_not_empty, "required": True},
                {"header": "Network", "key": "network", "validation_method": InputValidator.is_not_empty, "required": True},
                {"header": "Default Router", "key": "default_router", "validation_method": InputValidator.is_valid_ip, "required": False}
            ],
            action_buttons=pool_buttons,
            add_button_text="Add"
        )
        self.form_layout.insertWidget(1, self.pool_table)
        self.form_layout.insertSpacing(2, 30)
        self.form_layout.insertWidget(3, QLabel("<b>DHCP Excluded Addresses:</b>"))

        excl_buttons = [
            {"text": "Apply", "color": "#2e7d32", "method": self._on_apply_exclusion},
            {"text": "Delete", "color": "#d32f2f", "method": self._on_delete_exclusion}
        ]

        self.exclusion_table = ConfigTableWidget(
            columns=[
                {"header": "Start IP", "key": "start", "validation_method": InputValidator.is_valid_ip, "required": True},
                {"header": "End IP (Optional)", "key": "end", "validation_method": InputValidator.is_valid_ip, "required": False}
            ],
            action_buttons=excl_buttons,
            add_button_text="Add"
        )
        self.form_layout.insertWidget(4, self.exclusion_table)

    def populate_data(self, data: dict):
        """
        Populates the tables with parsed device data.
        """
        pools = [{"name": k, **v} for k, v in data.get("pools", {}).items()]
        self.pool_table.populate(pools)
        exclusions = [{"start": s or "", "end": e or ""} for s, e in data.get("excluded_addresses", [])]
        self.exclusion_table.populate(exclusions)

    def _on_apply_pool(self, button):
        """
        Extracts pool row data and emits apply signal.
        """
        row = self.pool_table.table.indexAt(button.parent().pos()).row()
        if self.pool_table._validate_row(row):
            data = self._get_row_data(self.pool_table, row)
            self.apply_pool_signal.emit(data)

    def _on_delete_pool(self, button):
        """
        Extracts pool row data and emits delete signal.
        """
        row = self.pool_table.table.indexAt(button.parent().pos()).row()
        data = self._get_row_data(self.pool_table, row)
        self.delete_pool_signal.emit(data)
        self.pool_table.table.removeRow(row)

    def _on_apply_exclusion(self, button):
        """
        Extracts exclusion row data and emits apply signal.
        """
        row = self.exclusion_table.table.indexAt(button.parent().pos()).row()
        if self.exclusion_table._validate_row(row):
            data = self._get_row_data(self.exclusion_table, row)
            self.apply_exclusion_signal.emit(data)

    def _on_delete_exclusion(self, button):
        """
        Extracts exclusion row data and emits delete signal.
        """
        row = self.exclusion_table.table.indexAt(button.parent().pos()).row()
        data = self._get_row_data(self.exclusion_table, row)
        self.delete_exclusion_signal.emit(data)
        self.exclusion_table.table.removeRow(row)

    def _get_row_data(self, table_widget, row):
        """
        Helper to extract data from a specific table row.
        """
        data = {col["key"]: table_widget.table.cellWidget(row, i).text() for i, col in enumerate(table_widget.columns)}
        data["_write_memory"] = self.write_memory_cb.isChecked()
        return data