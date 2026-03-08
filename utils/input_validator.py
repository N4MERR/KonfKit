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
    def is_in_range(value: str, min_val: int, max_val: int) -> bool:
        """
        Validates if the provided string is a number within the specified range.
        """
        if not value.isdigit():
            return False
        return min_val <= int(value) <= max_val

    @staticmethod
    def is_valid_ip(value: str) -> bool:
        """
        Validates if the provided string is a correctly formatted IPv4 address.
        """
        pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        return bool(re.match(pattern, value))

    @staticmethod
    def is_valid_ipv6(value: str) -> bool:
        """
        Validates if the provided string is a correctly formatted IPv6 address.
        """
        pattern = r"^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$"
        return bool(re.match(pattern, value, re.IGNORECASE))

    @staticmethod
    def is_valid_ipv6_prefix(value: str) -> bool:
        """
        Validates if the IPv6 prefix length is within the range 0-64.
        """
        clean_value = value.lstrip('/')
        if not clean_value.isdigit():
            return False
        return 0 <= int(clean_value) <= 64

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

    @staticmethod
    def is_valid_mac_address(value: str) -> bool:
        """
        Validates if the provided string is a valid MAC address in common Cisco formats.
        """
        pattern = r"^([0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4})$|^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
        return bool(re.match(pattern, value))

    @staticmethod
    def is_valid_interface_name(value: str) -> bool:
        """
        Validates if the provided string looks like a valid Cisco interface name.
        """
        pattern = r"^[A-Za-z]+[\s]?\d+(/\d+)*(\.\d+)?$"
        return bool(re.match(pattern, value))

    @staticmethod
    def is_not_empty(value: str) -> bool:
        """
        Validates that the string is not empty or just whitespace.
        """
        return bool(value and value.strip())