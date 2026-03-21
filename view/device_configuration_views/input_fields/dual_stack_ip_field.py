from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from view.device_configuration_views.input_fields.ip_address_field import IPAddressField
from view.device_configuration_views.input_fields.subnet_mask_field import SubnetMaskField
from view.device_configuration_views.input_fields.ipv6_address_field import IPv6AddressField
from view.device_configuration_views.input_fields.ipv6_prefix_length_field import IPv6PrefixLengthField


class DualStackIPField(QWidget):
    """
    A unified field set that manages both IPv4 and IPv6 configurations.
    Highlights all sub-fields if the minimum configuration requirement is not met.
    """

    def __init__(self, parent=None):
        """
        Initializes the dual-stack fields and hooks into child events to clear highlights.
        """
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        self.ipv4_field = IPAddressField("IPv4 Address:", is_optional=True)
        self.ipv4_mask_field = SubnetMaskField("IPv4 Subnet Mask:", is_optional=True, linked_ip_field=self.ipv4_field)

        self.ipv6_field = IPv6AddressField("IPv6 Address:", is_optional=True)
        self.ipv6_prefix_field = IPv6PrefixLengthField("IPv6 Prefix Length:", is_optional=True,
                                                       linked_ip_field=self.ipv6_field)

        self.sub_fields = [self.ipv4_field, self.ipv4_mask_field, self.ipv6_field, self.ipv6_prefix_field]

        for field in self.sub_fields:
            self.layout.addWidget(field)
            field.radio.toggled.connect(self.clear_highlight)
            field.input_widget.installEventFilter(self)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #d32f2f; font-size: 10pt; font-weight: bold;")
        self.error_label.hide()
        self.layout.addWidget(self.error_label)

    def validate(self) -> bool:
        """
        Ensures at least one stack is enabled. If not, highlights all components and displays the error.
        """
        self.clear_highlight()

        ipv4_enabled = self.ipv4_field.radio.isChecked()
        ipv6_enabled = self.ipv6_field.radio.isChecked()

        if not ipv4_enabled and not ipv6_enabled:
            self._apply_highlight("At least one type of ip address must be configured.")
            return False

        is_valid = True
        if ipv4_enabled:
            if not self.ipv4_field.validate() or not self.ipv4_mask_field.validate():
                is_valid = False

        if ipv6_enabled:
            if not self.ipv6_field.validate() or not self.ipv6_prefix_field.validate():
                is_valid = False

        return is_valid

    def _apply_highlight(self, message: str):
        """
        Visually highlights all internal fields to indicate a missing configuration group.
        """
        self.error_label.setText(message)
        self.error_label.show()
        for field in self.sub_fields:
            field.highlight_error("")
            field.error_label.hide()

    def clear_highlight(self):
        """
        Removes the error styling and hides the group message from all components.
        """
        self.error_label.hide()
        for field in self.sub_fields:
            field.clear_highlight()

    def eventFilter(self, source, event):
        """
        Detects interaction with child widgets to automatically clear group-level highlights.
        """
        from PySide6.QtCore import QEvent
        if event.type() in [QEvent.MouseButtonPress, QEvent.FocusIn]:
            self.clear_highlight()
        return super().eventFilter(source, event)

    def get_value(self) -> dict:
        """
        Exports a dictionary containing only the actively configured IP addresses and masks/prefixes.
        """
        return {
            "ipv4": self.ipv4_field.get_value() if self.ipv4_field.radio.isChecked() else None,
            "ipv4_mask": self.ipv4_mask_field.get_value() if self.ipv4_mask_field.radio.isChecked() else None,
            "ipv6": self.ipv6_field.get_value() if self.ipv6_field.radio.isChecked() else None,
            "ipv6_prefix": self.ipv6_prefix_field.get_value() if self.ipv6_prefix_field.radio.isChecked() else None
        }

    def reset(self):
        """
        Clears all inputs and unchecks radio toggles.
        """
        for field in self.sub_fields:
            field.reset()
        self.error_label.hide()