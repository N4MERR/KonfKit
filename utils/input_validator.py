import re

class InputValidator:
    """
    Provides static methods for validating various network-related input strings.
    """

    @staticmethod
    def is_valid_number(value: str) -> bool:
        """
        Validates if the provided string contains only numeric digits.
        """
        return value.isdigit()

    @staticmethod
    def is_valid_ip(value: str) -> bool:
        """
        Validates if the provided string is a correctly formatted IPv4 address.
        """
        pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        return bool(re.match(pattern, value))

    @staticmethod
    def is_valid_wildcard_mask(value: str) -> bool:
        """
        Validates if the provided string is a correct contiguous wildcard mask.
        """
        if not InputValidator.is_valid_ip(value):
            return False
        binary_str = "".join([bin(int(x))[2:].zfill(8) for x in value.split(".")])
        return bool(re.fullmatch(r"0*1*", binary_str))

    @staticmethod
    def is_valid_mask(value: str) -> bool:
        """
        Validates if the provided string is a correct contiguous subnet mask.
        """
        if not InputValidator.is_valid_ip(value):
            return False
        binary_str = "".join([bin(int(x))[2:].zfill(8) for x in value.split(".")])
        return bool(re.fullmatch(r"1*0*", binary_str))