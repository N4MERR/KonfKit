"""
Module defining project-specific exceptions for robust error handling.
"""

class CiscoToolError(Exception):
    """Base exception for all errors in the application."""
    pass

class ConnectionError(CiscoToolError):
    """Raised when serial or SSH connectivity fails."""
    pass

class DeviceTimeoutError(CiscoToolError):
    """Raised when a device fails to respond to a command in time."""
    pass

class AuthenticationError(CiscoToolError):
    """Raised specifically for SSH login failures."""
    pass

class IncorrectResponseException(CiscoToolError):
    """Raised when a device sends an unexpected CLI prompt."""
    pass