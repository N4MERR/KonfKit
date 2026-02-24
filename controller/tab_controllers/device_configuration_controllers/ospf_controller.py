from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController
from utils.input_validator import InputValidator

class OSPFController(BaseConfigController):
    """
    Controller handling validation and application for OSPF-specific configurations.
    """
    def handle_apply(self, data: dict):
        """
        Validates OSPF parameters and applies configuration to the device.
        """
        if self._validate(data):
            self._show_progress("Applying OSPF configuration...")
            self.model.apply_configuration(**data)
            self.view.clear_inputs()

    def handle_preview(self, data: dict):
        """
        Validates OSPF parameters and displays the generated commands for review.
        """
        if self._validate(data):
            super().handle_preview(data)

    def _validate(self, data: dict) -> bool:
        """
        Validates OSPF fields using the InputValidator and triggers view-side error highlighting.
        """
        errors = {}
        config_type = data.get("type")

        if not InputValidator.is_valid_number(data.get("process_id", "")):
            errors["process_id"] = "Invalid number"

        if config_type == "basic":
            if not InputValidator.is_valid_ip(data.get("network", "")):
                errors["network"] = "Invalid IP"
            if not InputValidator.is_valid_wildcard_mask(data.get("wildcard_mask", "")):
                errors["wildcard_mask"] = "Invalid mask"
            if not InputValidator.is_valid_number(data.get("area", "")):
                errors["area"] = "Invalid number"
        elif config_type == "router_id":
            if not InputValidator.is_valid_ip(data.get("router_id", "")):
                errors["router_id"] = "Invalid IP"
        elif config_type == "passive_interface":
            if not data.get("interface_name", "").strip():
                errors["interface_name"] = "Required"

        if errors:
            self.view.highlight_errors(errors)
            return False
        return True