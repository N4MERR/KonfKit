from view.device_configuration_views.base_config_view import BaseConfigView
from view.device_configuration_views.input_fields.acl_name_fields import NamedAclIdField, ExtendedAclIdField, \
    StandardAclIdField
from view.device_configuration_views.input_fields.dropdown_field import DropdownField
from view.device_configuration_views.input_fields.ip_address_field import IPAddressField
from view.device_configuration_views.input_fields.wildcard_mask_field import WildcardMaskField
from view.device_configuration_views.input_fields.number_field import NumberField


class ACLView(BaseConfigView):
    """
    View handling parameters for Access Control List configuration.
    """

    def __init__(self):
        """
        Initializes the ACL fields following mandated order and dynamic state linking.
        """
        super().__init__()

        self.add_field("acl_type",
                       DropdownField("ACL Type:", ["standard", "extended", "named standard", "named extended"],
                                     is_optional=False))

        self._create_acl_id_field()

        self.add_field("action", DropdownField("Action:", ["permit", "deny"], is_optional=False))

        self.add_field("source_type", DropdownField("Source Selection:", ["any", "host", "ip"], is_optional=False))
        self.add_field("source_ip", IPAddressField("Source IP Address:", is_optional=False))
        self.add_field("source_wildcard", WildcardMaskField("Source Wildcard Mask:", is_optional=False))

        self.add_field("protocol", DropdownField("Protocol:", ["ip", "tcp", "udp", "icmp"], is_optional=False))

        self.add_field("destination_type",
                       DropdownField("Destination Selection:", ["any", "host", "ip"], is_optional=False))
        self.add_field("destination_ip", IPAddressField("Destination IP Address:", is_optional=False))
        self.add_field("destination_wildcard", WildcardMaskField("Destination Wildcard Mask:", is_optional=False))

        self.add_field("port_operator",
                       DropdownField("Port Operator:", ["eq (equal)", "gt (greater)", "lt (less)", "ne (not equal)"],
                                     is_optional=True))
        self.add_field("port_number", NumberField("Port Number:", is_optional=True))

        self._setup_linked_fields()
        self._connect_signals()
        self._update_visibility()

    def _create_acl_id_field(self):
        """
        Creates the strictly validated ACL ID field dynamically based on the current ACL type.
        """
        acl_type = self.fields["acl_type"].get_value()

        if "named" in acl_type:
            field = NamedAclIdField("ACL Name:", is_optional=False)
            field.set_error_message("Name must start with a letter and contain no spaces or special characters.")
        elif "extended" in acl_type:
            field = ExtendedAclIdField("ACL Number (100-199 and 2000-2699):", is_optional=False)
            field.set_error_message("Extended ACL requires a number between 100-199 or 2000-2699.")
        else:
            field = StandardAclIdField("ACL Number (1-99 and 1300-1999):", is_optional=False)
            field.set_error_message("Standard ACL requires a number between 1-99 or 1300-1999.")

        self.fields["acl_id"] = field
        self.form_layout.insertWidget(1, field)

    def _remove_acl_id_field(self):
        """
        Removes the active ACL ID field from the layout and schedules it for deletion.
        """
        if "acl_id" in self.fields:
            field = self.fields.pop("acl_id")
            self.form_layout.removeWidget(field)
            field.deleteLater()

    def _on_acl_type_changed(self):
        """
        Rebuilds the ACL ID field and updates form visibility when the mode switches.
        """
        self._remove_acl_id_field()
        self._create_acl_id_field()
        self._update_visibility()

    def _setup_linked_fields(self):
        """
        Links the port_number state to port_operator, mirroring SSH IP/Mask logic.
        The port_number radio is disabled and visually synced with port_operator.
        """
        self.fields["port_number"].radio.setEnabled(False)
        self.fields["port_operator"].radio.toggled.connect(self._sync_port_number_state)
        self._sync_port_number_state(self.fields["port_operator"].radio.isChecked())

    def _sync_port_number_state(self, checked: bool):
        """
        Synchronizes the state of the port number field with the port operator field.
        """
        self.fields["port_number"].input_widget.setEnabled(checked)
        self.fields["port_number"].radio.setChecked(checked)
        if not checked:
            self.fields["port_number"].input_widget.clear()

    def _connect_signals(self):
        """
        Binds dropdown state changes to specific visibility update handlers.
        """
        type_field = self.fields.get("acl_type")
        if type_field and hasattr(type_field, "input_widget"):
            type_field.input_widget.currentIndexChanged.connect(self._on_acl_type_changed)

        for field_name in ["source_type", "destination_type", "port_operator"]:
            field = self.fields.get(field_name)
            if field and hasattr(field, "input_widget"):
                field.input_widget.currentIndexChanged.connect(self._update_visibility)

    def _update_visibility(self):
        """
        Evaluates selections and actively shows or hides related configuration fields.
        """
        acl_type = self.fields["acl_type"].get_value()
        source_type = self.fields["source_type"].get_value()
        dest_type = self.fields["destination_type"].get_value()

        is_extended = "extended" in acl_type

        self.fields["source_ip"].setVisible(source_type in ["host", "ip"])
        self.fields["source_wildcard"].setVisible(source_type == "ip")

        self.fields["protocol"].setVisible(is_extended)
        self.fields["destination_type"].setVisible(is_extended)

        if is_extended:
            self.fields["destination_ip"].setVisible(dest_type in ["host", "ip"])
            self.fields["destination_wildcard"].setVisible(dest_type == "ip")
            self.fields["port_operator"].setVisible(True)
            self.fields["port_number"].setVisible(True)
        else:
            self.fields["destination_ip"].setVisible(False)
            self.fields["destination_wildcard"].setVisible(False)
            self.fields["port_operator"].setVisible(False)
            self.fields["port_number"].setVisible(False)

    def validate_all(self) -> bool:
        """
        Overrides base validation to only enforce checks on actively visible fields.
        """
        is_valid = True
        for field in self.fields.values():
            if field.isVisible() and hasattr(field, 'validate'):
                if not field.validate():
                    is_valid = False
        return is_valid

    def get_data(self) -> dict:
        """
        Gathers formatted payload dictionary targeting visible field values.
        """
        return {
            "acl_type": self.fields["acl_type"].get_value(),
            "acl_id": self.fields["acl_id"].get_value(),
            "action": self.fields["action"].get_value(),
            "protocol": self.fields["protocol"].get_value(),
            "source_type": self.fields["source_type"].get_value(),
            "source_ip": self.fields["source_ip"].get_value(),
            "source_wildcard": self.fields["source_wildcard"].get_value(),
            "destination_type": self.fields["destination_type"].get_value(),
            "destination_ip": self.fields["destination_ip"].get_value(),
            "destination_wildcard": self.fields["destination_wildcard"].get_value(),
            "port_operator": self.fields["port_operator"].get_value(),
            "port_number": self.fields["port_number"].get_value(),
            "_save_configuration": self.save_configuration_cb.isChecked()
        }