import json
import os
import paramiko
import threading
import time
import logging
from PySide6.QtCore import QObject, Signal
from utils.exceptions import AuthenticationError, ConnectionError

logger = logging.getLogger(__name__)

class SSHConnectionManager(QObject):
    """
    Manages SSH connection profiles and active interactive shell sessions.
    """
    connections_updated = Signal()
    data_received = Signal(str)
    connection_lost = Signal(str)

    def __init__(self, filename="ssh_connections.json"):
        super().__init__()
        self.filename = filename
        self.connections = self.load_connections()
        self.ssh_client = None
        self.shell = None
        self._receiving = False

    def load_connections(self):
        """Loads SSH profiles from a JSON file with integrity checking."""
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load connections: {e}")
            return []

    def save_connection(self, name, host, username, password):
        """Adds a new connection profile and persists it to disk."""
        self.connections.append({
            "name": name,
            "host": host,
            "username": username,
            "password": password
        })
        self._write_to_file()
        self.connections_updated.emit()

    def delete_connection(self, index):
        """Removes a connection profile at the specified index."""
        if 0 <= index < len(self.connections):
            self.connections.pop(index)
            self._write_to_file()
            self.connections_updated.emit()

    def _write_to_file(self):
        """Saves the current connection list to the JSON storage file."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.connections, f, indent=4)
        except IOError as e:
            logger.error(f"Failed to write to {self.filename}: {e}")

    def connect_ssh(self, host, username, password):
        """Establishes an SSH connection and initializes a shell."""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(hostname=host, username=username, password=password, timeout=10)
            self.shell = self.ssh_client.invoke_shell()
            self._receiving = True
            threading.Thread(target=self._read_output, daemon=True).start()
            return True
        except paramiko.AuthenticationException:
            self.connection_lost.emit("Invalid username or password.")
            return False
        except (paramiko.SSHException, Exception) as e:
            self.connection_lost.emit(f"Connection error: {str(e)}")
            return False

    def _read_output(self):
        """Continuously polls the shell for incoming data."""
        while self._receiving:
            try:
                if self.shell and self.shell.recv_ready():
                    data = self.shell.recv(4096).decode('utf-8', errors='ignore')
                    self.data_received.emit(data)
                time.sleep(0.01)
            except Exception:
                self._receiving = False
                self.connection_lost.emit("Connection lost during data transfer.")

    def send_input(self, text):
        """Transmits keyboard input to the remote shell session."""
        if self.shell and self.shell.send_ready():
            try:
                self.shell.send(text)
            except Exception as e:
                logger.error(f"Input transmission failed: {e}")

    def close_connection(self):
        """Gracefully shuts down the shell and the SSH client."""
        self._receiving = False
        if self.shell:
            self.shell.close()
        if self.ssh_client:
            self.ssh_client.close()