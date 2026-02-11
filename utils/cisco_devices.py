import json
import os
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class BootEnvironment(Enum):
    ROMMON = "ROMMON"
    SWITCH_BOOTLOADER = "SWITCH_BOOTLOADER"


@dataclass(frozen=True)
class Device:
    model: str
    category: str
    boot_environment: BootEnvironment


class Devices:
    """
    Handles loading and filtering of Cisco devices from an external JSON file.
    """
    _devices = []

    @classmethod
    def load_from_json(cls, file_path="devices.json"):
        """Loads devices into memory with robust exception handling."""
        if not os.path.exists(file_path):
            logger.warning(f"Device file not found: {file_path}")
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                if not isinstance(data, dict) or 'devices' not in data:
                    raise ValueError("JSON root must be an object containing a 'devices' list")

                new_devices = []
                for entry in data['devices']:
                    try:
                        new_devices.append(Device(
                            model=entry['model'],
                            category=entry['category'],
                            boot_environment=BootEnvironment(entry['boot_env'])
                        ))
                    except (KeyError, ValueError) as e:
                        logger.error(f"Skipping invalid device entry: {entry}. Error: {e}")

                cls._devices = new_devices

        except json.JSONDecodeError as e:
            logger.critical(f"Failed to parse {file_path}: Invalid JSON syntax. {e}")
            cls._devices = []
        except Exception as e:
            logger.critical(f"Unexpected error loading devices: {e}")
            cls._devices = []

        return cls._devices

    @classmethod
    def get_all(cls):
        if not cls._devices:
            cls.load_from_json()
        return cls._devices

    @classmethod
    def get_routers(cls):
        return [d for d in cls.get_all() if d.category == "Router"]

    @classmethod
    def get_switches(cls):
        return [d for d in cls.get_all() if d.category == "Switch"]