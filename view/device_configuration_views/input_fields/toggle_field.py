# rocnikovy_projekt_new/view/device_configuration_views/input_fields/toggle_field.py
from PySide6.QtWidgets import QRadioButton
from view.device_configuration_views.input_fields.base_input_field import BaseInputField

class ToggleField(BaseInputField):
    """
    A binary toggle field component for the standard configuration UI.
    Overrides connection logic to prevent textChanged signal errors.
    """
    def _create_input_widget(self) -> QRadioButton:
        """
        Creates and returns a QRadioButton as the primary input widget.
        """
        widget = QRadioButton()
        return widget

    def _setup_connections(self):
        """
        Overrides BaseInputField's connection logic.
        Connects the toggled signal instead of textChanged to avoid AttributeErrors.
        """
        self.input_widget.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked: bool):
        """
        Syncs the radio indicator state when the toggle is interacted with.
        """
        self.radio.setChecked(checked)

    def isChecked(self) -> bool:
        """
        Returns the current checked state of the toggle.
        """
        return self.input_widget.isChecked()

    def setChecked(self, checked: bool):
        """
        Sets the checked state of the toggle.
        """
        self.input_widget.setChecked(checked)

    def get_value(self) -> bool:
        """
        Returns the boolean value for the configuration model.
        """
        return self.isChecked()