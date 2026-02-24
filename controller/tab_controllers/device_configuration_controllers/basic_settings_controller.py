"""
Controller handling validation and application of basic device settings.
"""
from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController


class BasicSettingsController(BaseConfigController):
    """
    Controller handling validation and application of basic device settings.
    """

    def handle_apply(self, data: dict):
        """
        Validates the input data before requesting the model to apply the configuration.
        """
        if self._validate(data):
            self._show_progress("Applying basic settings...")
            self.model.apply_configuration(**data)

    def handle_preview(self, data: dict):
        """
        Validates the input data before showing the configuration preview dialog.
        """
        if self._validate(data):
            super().handle_preview(data)

    def _validate(self, data: dict) -> bool:
        """
        Checks for required fields and password matching, triggering view highlights if errors exist.
        """
        errors = {}
        if data["hostname_enabled"] and not data["hostname"].strip():
            errors["hostname"] = "Required"
        if data["secret_enabled"]:
            if not data["secret"]:
                errors["secret"] = "Required"
            elif data["secret"] != data["confirm_secret"]:
                errors["confirm"] = "Passwords do not match"
        if data["banner_enabled"] and not data["banner"].strip():
            errors["banner"] = "Required"

        if errors:
            self.view.highlight_errors(errors)
            return False
        return True