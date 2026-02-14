import json
import os
import logging
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class ProfileManager(QObject):
    """
    Manages the loading, saving, and deletion of connection profiles for SSH, Telnet, and Serial protocols.
    Persists data to a JSON file.
    """
    profiles_updated = Signal()

    def __init__(self, filename="connections.json"):
        super().__init__()
        self.filename = filename
        self.profiles = self.load_profiles()

    def load_profiles(self):
        """
        Loads connection profiles from the JSON file.
        Returns an empty list if the file does not exist or is invalid.
        """
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load profiles: {e}")
            return []

    def save_profile(self, profile_data):
        """
        Saves a new profile or updates an existing one based on the name and protocol.
        """
        existing_index = -1
        for i, profile in enumerate(self.profiles):
            if profile['name'] == profile_data['name'] and profile['protocol'] == profile_data['protocol']:
                existing_index = i
                break

        if existing_index >= 0:
            self.profiles[existing_index] = profile_data
        else:
            self.profiles.append(profile_data)

        self._write_to_file()
        self.profiles_updated.emit()

    def delete_profile(self, name, protocol):
        """
        Removes a profile matching the given name and protocol.
        """
        initial_count = len(self.profiles)
        self.profiles = [p for p in self.profiles if not (p['name'] == name and p['protocol'] == protocol)]

        if len(self.profiles) < initial_count:
            self._write_to_file()
            self.profiles_updated.emit()

    def _write_to_file(self):
        """
        Writes the current list of profiles to the JSON file.
        """
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.profiles, f, indent=4)
        except IOError as e:
            logger.error(f"Failed to write to {self.filename}: {e}")

    def get_profiles(self):
        """
        Returns the current list of loaded profiles.
        """
        return self.profiles