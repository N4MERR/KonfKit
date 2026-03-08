import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class BootEnvironment(Enum):
    """
    Enumeration of supported Cisco boot environments for password recovery.
    """
    ROMMON = "ROMMON"
    SWITCH_BOOTLOADER = "SWITCH_BOOTLOADER"

@dataclass(frozen=True)
class Device:
    """
    Data container representing a Cisco hardware device and its recovery environment.
    """
    model: str
    category: str
    boot_environment: BootEnvironment

class Devices:
    """
    Handles management and filtering of supported Cisco devices.
    The device list is hardcoded to ensure availability across all modules.
    """
    _devices = [
        Device(model="ISR 4321", category="Router", boot_environment=BootEnvironment.ROMMON),
        Device(model="ISR 4331", category="Router", boot_environment=BootEnvironment.ROMMON),
        Device(model="ISR 4351", category="Router", boot_environment=BootEnvironment.ROMMON),
        Device(model="ASR 1001-X", category="Router", boot_environment=BootEnvironment.ROMMON),
        Device(model="ASR 1002-X", category="Router", boot_environment=BootEnvironment.ROMMON),
        Device(model="Catalyst 2950", category="Switch", boot_environment=BootEnvironment.SWITCH_BOOTLOADER),
        Device(model="Catalyst 2960", category="Switch", boot_environment=BootEnvironment.SWITCH_BOOTLOADER),
        Device(model="Catalyst 2960X", category="Switch", boot_environment=BootEnvironment.SWITCH_BOOTLOADER),
        Device(model="Catalyst 3560", category="Switch", boot_environment=BootEnvironment.SWITCH_BOOTLOADER),
        Device(model="Catalyst 3750", category="Switch", boot_environment=BootEnvironment.SWITCH_BOOTLOADER)
    ]

    @classmethod
    def get_all(cls):
        """
        Retrieves the complete list of supported devices.
        """
        return cls._devices

    @classmethod
    def get_routers(cls):
        """
        Retrieves devices categorized specifically as routers.
        """
        return [d for d in cls._devices if d.category == "Router"]

    @classmethod
    def get_switches(cls):
        """
        Retrieves devices categorized specifically as switches.
        """
        return [d for d in cls._devices if d.category == "Switch"]