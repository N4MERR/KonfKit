from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt
from view.device_configuration_views.input_fields.base_input_field import BaseInputField


class MultiSelectListField(BaseInputField):
    """
    Input field providing a list of checkable items for multiple selection with enforced limits.
    """

    def __init__(self, label_text, is_optional=False, min_selections=1, max_selections=None, parent=None):
        """
        Initializes the multi-select field with boundary constraints.
        """
        self.min_selections = min_selections
        self.max_selections = max_selections
        super().__init__(label_text, is_optional, parent)

    def _create_input_widget(self):
        """
        Overrides the base method to instantiate a QListWidget tightly constrained to be exactly 5 elements tall.
        """
        widget = QListWidget()
        widget.setFixedHeight(110)
        return widget

    def _setup_connections(self):
        """
        Overrides the base connection setup to link list-specific item interaction signals.
        """
        self.input_widget.itemChanged.connect(self._on_item_changed)
        self.input_widget.itemChanged.connect(lambda: self.clear_highlight())

    def _on_item_changed(self, item):
        """
        Automatically enables the field's radio indicator if any list items become checked.
        """
        if self.get_value() and not self.radio.isChecked():
            self.radio.setChecked(True)

    def populate_items(self, items: list[str]):
        """
        Populates the list widget with checkable items.
        """
        self.input_widget.clear()
        for item_text in items:
            item = QListWidgetItem(item_text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.input_widget.addItem(item)

    def get_value(self) -> list[str]:
        """
        Retrieves a list of all currently checked item strings.
        """
        selected_items = []
        for index in range(self.input_widget.count()):
            item = self.input_widget.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                selected_items.append(item.text())
        return selected_items

    def reset(self):
        """
        Unchecks all items in the list widget cleanly.
        """
        self.input_widget.blockSignals(True)
        for index in range(self.input_widget.count()):
            item = self.input_widget.item(index)
            item.setCheckState(Qt.CheckState.Unchecked)
        self.input_widget.blockSignals(False)
        self.radio.setChecked(False)
        self.clear_highlight()

    def _run_validation(self, value: list[str]) -> bool:
        """
        Validates that the selected items fall within the defined minimum and maximum constraints.
        """
        if not self.is_optional and not value:
            self.error_message = f"At least {self.min_selections} element(s) must be selected."
            return False

        if value:
            if len(value) < self.min_selections:
                self.error_message = f"At least {self.min_selections} element(s) must be selected."
                return False

            if self.max_selections and len(value) > self.max_selections:
                self.error_message = f"Maximum of {self.max_selections} elements allowed."
                return False

        return True