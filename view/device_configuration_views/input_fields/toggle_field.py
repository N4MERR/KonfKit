# rocnikovy_projekt_new/view/device_configuration_views/input_fields/toggle_field.py
from PySide6.QtWidgets import QRadioButton
from PySide6.QtCore import Signal
from view.device_configuration_views.input_fields.base_input_field import BaseInputField

class ToggleField(BaseInputField):
    """
    A binary toggle field component for the standard configuration UI.
    Proxies the toggled signal from the underlying RadioButton.
    """
    toggled = Signal(bool)

    def _create_input_widget(self) -> QRadioButton:
        """
        Creates and returns a QRadioButton as the primary input widget.
        """
        widget = QRadioButton()
        return widget

    def _setup_connections(self):
        """
        Overrides the base connection setup to avoid textChanged signal errors.
        Links the internal widget signal to the class proxy signal and state synchronization.
        """
        self.input_widget.toggled.connect(self._on_toggled_internal)

    def _on_toggled_internal(self, checked: bool):
        """
        Syncs the radio indicator state and emits the public proxy signal.
        """
        self.radio.setChecked(checked)
        self.toggled.emit(checked)

    def isChecked(self) -> bool:
        """
        Returns the current checked state of the internal widget.
        """
        return self.input_widget.isChecked()

    def setChecked(self, checked: bool):
        """
        Updates the checked state of the internal widget.
        """
        self.input_widget.setChecked(checked)

    def get_value(self) -> bool:
        """
        Returns the boolean value for configuration generation.
        """
        return self.isChecked()