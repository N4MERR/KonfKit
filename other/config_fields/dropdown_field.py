from PySide6.QtWidgets import QComboBox
from .base_config_field import BaseConfigField

class DropdownField(BaseConfigField):
    """
    Field using a QComboBox for selection.
    """

    def __init__(self, label_text, options, is_optional=False, parent=None):
        """
        Initializes the dropdown field with options.
        """
        self.options = options
        super().__init__(label_text, is_optional, parent)

    def _create_input_widget(self):
        """
        Creates a combobox as the input widget.
        """
        combo = QComboBox()
        combo.addItems(self.options)
        return combo