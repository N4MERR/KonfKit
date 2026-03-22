from PySide6.QtWidgets import QComboBox
from .base_input_field import BaseInputField


class NoScrollComboBox(QComboBox):
    """
    Custom QComboBox that ignores mouse wheel events and disables automatic mouse-hover scrolling.
    """

    def __init__(self, parent=None):
        """
        Initializes the combobox and configures the internal view to disable automatic boundary scrolling.
        """
        super().__init__(parent)

        self.view().setAutoScroll(False)

    def wheelEvent(self, event):
        """
        Overrides the default wheel event to prevent the combobox from changing values on scroll.
        The event is ignored so it can propagate to the parent scroll area.
        """
        event.ignore()


class DropdownField(BaseInputField):
    """
    Field using a custom QComboBox that prevents accidental scrolling and automatic list movement.
    """

    def __init__(self, label_text, options, is_optional=False, parent=None):
        """
        Initializes the dropdown field with the provided options.
        """
        self.options = options
        super().__init__(label_text, is_optional, parent)

    def _create_input_widget(self):
        """
        Creates a custom NoScrollComboBox as the input widget.
        """
        combo = NoScrollComboBox()
        combo.addItems(self.options)
        return combo