"""
Controller linking the Telnet view with the Telnet model.
"""
from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController


class TelnetController(BaseConfigController):
    """
    Controller handling validation and execution requests for Telnet configurations.
    """

    def handle_apply(self, data: dict):
        """
        Validates Telnet form data before requesting model execution.
        """
        if self._validate(data):
            self._show_progress("Applying Telnet configuration...")
            self.model.apply_configuration(**data)

    def handle_preview(self, data: dict):
        """
        Validates Telnet form data before displaying the command preview window.
        """
        if self._validate(data):
            super().handle_preview(data)

    def _validate(self, data: dict) -> bool:
        """
        Validates VTY bounds and local login credentials.
        """
        errors = {}
        try:
            start = int(data.get("vty_start", ""))
            end = int(data.get("vty_end", ""))
            if start > end or start < 0 or end > 15:
                errors["vty"] = "Invalid VTY range"
        except ValueError:
            errors["vty"] = "Must be numeric"

        if data.get("local_login"):
            if not data.get("username", "").strip():
                errors["username"] = "Required for local login"
            if not data.get("password", "").strip():
                errors["password"] = "Required for local login"

        if errors:
            self.view.highlight_errors(errors)
            return False
        return True