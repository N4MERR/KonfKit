"""
Controller linking the SSH view with the SSH model.
"""
from controller.tab_controllers.device_configuration_controllers.base_config_controller import BaseConfigController


class SSHController(BaseConfigController):
    """
    Controller handling validation and execution requests for SSH configurations.
    """

    def handle_apply(self, data: dict):
        """
        Validates SSH form data before requesting model execution.
        """
        if self._validate(data):
            self._show_progress("Applying SSH configuration...")
            self.model.apply_configuration(**data)

    def handle_preview(self, data: dict):
        """
        Validates SSH form data before displaying the command preview window.
        """
        if self._validate(data):
            super().handle_preview(data)

    def _validate(self, data: dict) -> bool:
        """
        Validates domain necessity, VTY bounds, and local login credentials.
        """
        errors = {}
        if not data.get("domain", "").strip():
            errors["domain"] = "Required for SSH keys"

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