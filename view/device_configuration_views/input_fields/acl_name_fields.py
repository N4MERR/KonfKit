import re

from view.device_configuration_views.input_fields.base_input_field import BaseInputField


class StandardAclIdField(BaseInputField):
    """
    Input field enforcing Cisco standard ACL numbering rules.
    """
    def _run_validation(self, value):
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
    def _run_validation(self, value):
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
    def _run_validation(self, value):
        if not value or not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", value):
            return False
        return True