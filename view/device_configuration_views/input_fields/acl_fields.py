import re

from view.device_configuration_views.input_fields.base_input_field import BaseInputField


class StandardAclIdField(BaseInputField):
    """
    Input field enforcing Cisco standard ACL numbering rules.
    """

    def __init__(self, label_text, is_optional=False, parent=None):
        """
        Initializes the standard ACL ID field with a specific error message.
        """
        super().__init__(label_text, is_optional, parent)
        self.error_message = "Invalid Standard ACL ID (1-99 or 1300-1999)"

    def _run_validation(self, value):
        """
        Validates the standard ACL range.
        """
        if not value:
            return False
        try:
            num = int(value)
            return (1 <= num <= 99) or (1300 <= num <= 1999)
        except ValueError:
            return False


class ExtendedAclIdField(BaseInputField):
    """
    Input field enforcing Cisco extended ACL numbering rules.
    """

    def __init__(self, label_text, is_optional=False, parent=None):
        """
        Initializes the extended ACL ID field with a specific error message.
        """
        super().__init__(label_text, is_optional, parent)
        self.error_message = "Invalid Extended ACL ID (100-199 or 2000-2699)"

    def _run_validation(self, value):
        """
        Validates the extended ACL range.
        """
        if not value:
            return False
        try:
            num = int(value)
            return (100 <= num <= 199) or (2000 <= num <= 2699)
        except ValueError:
            return False


class NamedAclIdField(BaseInputField):
    """
    Input field enforcing Cisco named ACL string rules.
    """

    def __init__(self, label_text, is_optional=False, parent=None):
        """
        Initializes the named ACL field with a specific error message.
        """
        super().__init__(label_text, is_optional, parent)
        self.error_message = "Invalid Named ACL (must start with letter, alphanumeric only)"

    def _run_validation(self, value):
        """
        Validates the named ACL string format.
        """
        if not value or not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", value):
            return False
        return True