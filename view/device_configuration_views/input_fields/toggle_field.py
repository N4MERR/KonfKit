from PySide6.QtWidgets import QRadioButton
from .base_input_field import BaseConfigField

class ToggleField(BaseConfigField):
    """
    A simple checkable field for binary settings like 'Shutdown' or 'Routing Enabled'.
    """

    def _create_input_widget(self):
        """
        Creates a radio button as the primary input widget.
        """
        self.option = QRadioButton("Enabled")
        return self.option

    def get_value(self):
        """
        Retrieves the boolean state of the radio button.
        """
        return self.option.isChecked()

    def _run_validation(self, value):
        """
        Validates the toggle field. Always returns True.
        """
        return True