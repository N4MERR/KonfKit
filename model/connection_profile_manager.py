import json
import os
import logging
import keyring
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class ProfileManager(QObject):
    """
    Manages the loading, saving, and deletion of connection profiles using Netmiko-compatible keys.
    Integrates with the operating system's native credential manager (Keyring) to securely store passwords.
    """
    profiles_updated = Signal()

    def __init__(self, filename="connections.json", service_name="NetworkConnectionApp"):
        """
        Initializes the ProfileManager with the JSON filename and the Keyring service name.
        """
        super().__init__()
        self.filename = filename
        self.service_name = service_name
        self.profiles = self.load_profiles()

    def load_profiles(self):
        """
        Loads connection profiles from the JSON file and fetches sensitive fields from the OS Keyring.
        """
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for profile in data:
                        pwd = keyring.get_password(self.service_name,
                                                   f"{profile['name']}_{profile['device_type']}_password")
                        if pwd:
                            profile['password'] = pwd

                        secret = keyring.get_password(self.service_name,
                                                      f"{profile['name']}_{profile['device_type']}_secret")
                        if secret:
                            profile['secret'] = secret
                    return data
                return []
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load profiles: {e}")
            return []

    def save_profile(self, profile_data):
        """
        Saves or updates a profile in memory, pushes credentials to the OS Keyring, and writes safe data to JSON.
        """
        existing_index = -1
        for i, profile in enumerate(self.profiles):
            if profile['name'] == profile_data['name'] and profile['device_type'] == profile_data['device_type']:
                existing_index = i
                break

        if existing_index >= 0:
            self.profiles[existing_index] = profile_data
        else:
            self.profiles.append(profile_data)

        if profile_data.get('password'):
            keyring.set_password(self.service_name, f"{profile_data['name']}_{profile_data['device_type']}_password",
                                 profile_data['password'])

        if profile_data.get('secret'):
            keyring.set_password(self.service_name, f"{profile_data['name']}_{profile_data['device_type']}_secret",
                                 profile_data['secret'])

        self._write_to_file()
        self.profiles_updated.emit()

    def delete_profile(self, name, device_type):
        """
        Removes a profile from memory, deletes its Keyring credentials, and updates the JSON file.
        """
        initial_count = len(self.profiles)
        self.profiles = [p for p in self.profiles if not (p['name'] == name and p['device_type'] == device_type)]

        if len(self.profiles) < initial_count:
            try:
                keyring.delete_password(self.service_name, f"{name}_{device_type}_password")
            except keyring.errors.PasswordDeleteError:
                pass

            try:
                keyring.delete_password(self.service_name, f"{name}_{device_type}_secret")
            except keyring.errors.PasswordDeleteError:
                pass

            self._write_to_file()
            self.profiles_updated.emit()

    def _write_to_file(self):
        """
        Strips passwords and secrets from the profile dictionaries before saving them to the JSON file.
        """
        safe_profiles = []
        for profile in self.profiles:
            safe_profile = profile.copy()
            safe_profile.pop('password', None)
            safe_profile.pop('secret', None)
            safe_profiles.append(safe_profile)

        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(safe_profiles, f, indent=4)
        except IOError as e:
            logger.error(f"Failed to write to {self.filename}: {e}")

    def get_profiles(self):
        """
        Returns the current list of loaded profiles.
        """
        return self.profiles