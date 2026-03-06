from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox

class RadioIndicatorField(QWidget):
    """
    A standalone checkbox field for binary global settings.
    """

    def __init__(self, label_text, parent=None):
        """
        Initializes the standalone checkbox indicator field.
        """
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 10)
        self.radio = QCheckBox(label_text)
        self.layout.addWidget(self.radio)

    def isChecked(self):
        """
        Retrieves the boolean state of the checkbox.
        """
        return self.radio.isChecked()