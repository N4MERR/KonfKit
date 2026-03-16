from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout
from view.device_configuration_views.base_config_view import BaseConfigView


class VLANView(BaseConfigView):
    """
    Dynamic view for listing, editing, and applying VLAN configurations.
    """

    def __init__(self):
        """
        Initializes the VLAN view with a data table overriding static fields.
        """
        super().__init__()

        self.vlan_table = QTableWidget(0, 2)
        self.vlan_table.setHorizontalHeaderLabels(["VLAN ID", "VLAN Name"])
        self.vlan_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.form_layout.addWidget(self.vlan_table)

        self.table_controls = QHBoxLayout()
        self.add_row_btn = QPushButton("Add VLAN")
        self.remove_row_btn = QPushButton("Remove Selected")

        self.table_controls.addWidget(self.add_row_btn)
        self.table_controls.addWidget(self.remove_row_btn)
        self.form_layout.addLayout(self.table_controls)

        self.add_row_btn.clicked.connect(self._add_empty_row)
        self.remove_row_btn.clicked.connect(self._remove_selected_row)

    def populate_data(self, data: dict):
        """
        Fills the table with VLANs loaded from the device.
        """
        self.vlan_table.setRowCount(0)
        vlans = data.get("vlans", {})
        for row, (vlan_id, name) in enumerate(vlans.items()):
            self.vlan_table.insertRow(row)
            self.vlan_table.setItem(row, 0, QTableWidgetItem(str(vlan_id)))
            self.vlan_table.setItem(row, 1, QTableWidgetItem(name))

    def get_data(self) -> dict:
        """
        Extracts the current table state to send to the controller.
        """
        vlans = {}
        for row in range(self.vlan_table.rowCount()):
            vlan_id_item = self.vlan_table.item(row, 0)
            name_item = self.vlan_table.item(row, 1)
            if vlan_id_item and vlan_id_item.text():
                vlans[vlan_id_item.text()] = name_item.text() if name_item else ""

        return {
            "type": "vlan_batch",
            "vlans": vlans,
            "_save_configuration": self.save_configuration_cb.isChecked()
        }

    def _add_empty_row(self):
        """
        Appends a blank row to the table for a new VLAN.
        """
        row_position = self.vlan_table.rowCount()
        self.vlan_table.insertRow(row_position)

    def _remove_selected_row(self):
        """
        Removes the currently selected row from the table.
        """
        current_row = self.vlan_table.currentRow()
        if current_row >= 0:
            self.vlan_table.removeRow(current_row)

    def validate_all(self):
        """
        Bypasses default validation since data is table-based.
        """
        return True