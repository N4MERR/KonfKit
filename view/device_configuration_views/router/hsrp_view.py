from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal
from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.input_fields.dropdown_field import DropdownField
from view.device_configuration_views.input_fields.number_field import NumberField
from view.device_configuration_views.input_fields.adaptive_ip_address_field import AdaptiveIPAddressField
from view.device_configuration_views.input_fields.toggle_field import ToggleField


class HSRPView(BaseConfigView):
    """
    View handling dual-stack HSRP (Hot Standby Router Protocol) configuration.
    """
    load_interfaces_signal = Signal()

    def __init__(self):
        """
        Initializes HSRP configuration UI components including an adaptive Virtual IP field.
        """
        super().__init__()

        self.load_interfaces_btn = QPushButton("Load Interfaces")
        self.load_interfaces_btn.setStyleSheet(
            "QPushButton { background-color: #cccccc; color: black; border: 1px solid #8a8886; border-radius: 4px; padding: 6px; font-weight: bold; }"
            "QPushButton:hover { background-color: #b3b3b3; }"
            "QPushButton:disabled { background-color: #e6e6e6; color: #a0a0a0; border: 1px solid #c0c0c0; }"
        )
        self.load_interfaces_btn.clicked.connect(self.load_interfaces_signal.emit)
        self.button_layout.insertWidget(0, self.load_interfaces_btn)

        self.add_field("interface", DropdownField("Target Interface:", [], is_optional=False))
        self.add_field("group_id", NumberField("Standby Group ID:", is_optional=False))

        self.virtual_ip_field = AdaptiveIPAddressField("Virtual IP Address:", is_optional=False)
        self.add_field("virtual_ip", self.virtual_ip_field)

        self.add_field("priority", NumberField("Priority (0-255):", is_optional=True))
        self.add_field("preempt", ToggleField("Enable Preempt:", is_optional=False))

    def update_interfaces(self, interfaces: list[str]):
        """
        Updates the interface dropdown with retrieved device data.
        """
        self.fields["interface"].input_widget.clear()
        self.fields["interface"].input_widget.addItems(interfaces)

    def get_data(self) -> dict:
        """
        Retrieves HSRP configuration data including the detected IP protocol version.
        """
        return {
            "type": "hsrp",
            "interface": self.fields["interface"].get_value(),
            "group_id": self.fields["group_id"].get_value(),
            "virtual_ip": self.virtual_ip_field.get_value(),
            "version": self.virtual_ip_field.get_ip_version(),
            "priority": self.fields["priority"].get_value() if self.fields["priority"].radio.isChecked() else None,
            "preempt": self.fields["preempt"].get_value(),
            "_save_configuration": self.save_configuration_cb.isChecked()
        }