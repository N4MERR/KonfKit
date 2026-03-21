from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal
from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.input_fields.dropdown_field import DropdownField
from view.device_configuration_views.input_fields.number_field import NumberField
from view.device_configuration_views.input_fields.dual_stack_ip_field import DualStackIPField


class RouterPhysicalInterfaceView(BaseConfigView):
    """
    View handling physical router interface settings.
    """
    load_interfaces_signal = Signal()

    def __init__(self):
        """
        Initializes physical interface configuration UI components.
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

        self.add_field("interface", DropdownField("Interface:", [], is_optional=False))

        self.dual_stack_ip = DualStackIPField()
        self.add_field("ip_config", self.dual_stack_ip)

    def update_interfaces(self, interfaces: list[str]):
        """
        Updates the interface dropdown with retrieved device data.
        """
        self.fields["interface"].input_widget.clear()
        self.fields["interface"].input_widget.addItems(interfaces)

    def get_data(self) -> dict:
        """
        Retrieves interface configuration data including the bundled IP definitions.
        """
        return {
            "type": "router_physical_interface",
            "interface": self.fields["interface"].get_value(),
            "ip_config": self.fields["ip_config"].get_value(),
            "_save_configuration": self.save_configuration_cb.isChecked()
        }


class RouterSubinterfaceView(BaseConfigView):
    """
    View handling 802.1Q router subinterface settings.
    """
    load_interfaces_signal = Signal()

    def __init__(self):
        """
        Initializes subinterface configuration UI components.
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

        self.add_field("interface", DropdownField("Parent Interface:", [], is_optional=False))
        self.add_field("subinterface", NumberField("Subinterface ID:", is_optional=False))
        self.add_field("vlan", NumberField("VLAN ID (802.1Q):", is_optional=False))

        self.dual_stack_ip = DualStackIPField()
        self.add_field("ip_config", self.dual_stack_ip)

    def update_interfaces(self, interfaces: list[str]):
        """
        Updates the interface dropdown with retrieved device data.
        """
        self.fields["interface"].input_widget.clear()
        self.fields["interface"].input_widget.addItems(interfaces)

    def get_data(self) -> dict:
        """
        Retrieves subinterface configuration data including the bundled IP definitions.
        """
        return {
            "type": "router_subinterface",
            "interface": self.fields["interface"].get_value(),
            "subinterface": self.fields["subinterface"].get_value(),
            "vlan": self.fields["vlan"].get_value(),
            "ip_config": self.fields["ip_config"].get_value(),
            "_save_configuration": self.save_configuration_cb.isChecked()
        }


class RouterInterfaceView:
    """
    Container view holding physical and subinterface configuration panes.
    """

    def __init__(self):
        """
        Initializes both physical and subinterface view instances.
        """
        self.physical = RouterPhysicalInterfaceView()
        self.subinterface = RouterSubinterfaceView()