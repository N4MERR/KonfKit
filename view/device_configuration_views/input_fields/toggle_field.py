from PySide6.QtWidgets import QCheckBox
from PySide6.QtCore import Signal
from view.device_configuration_views.input_fields.base_input_field import BaseInputField


class ToggleField(BaseInputField):
    """
    A binary toggle field component for the standard configuration UI utilizing a checkbox.
    Proxies the toggled signal from the underlying QCheckBox.
    """
    toggled = Signal(bool)

    def _create_input_widget(self) -> QCheckBox:
        """
        Creates and returns a QCheckBox as the primary input widget.
        """
        widget = QCheckBox()
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
        if hasattr(self, 'radio') and self.radio:
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