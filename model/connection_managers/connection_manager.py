import json
import os
import logging
import serial
import paramiko
import telnetlib
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

class ConnectionManager(QObject):
    connections_updated = Signal()

    def __init__(self, filename="connections.json"):
        super().__init__()
        self.filename = filename
        self.connections = self.load_connections()

    def load_connections(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load connections: {e}")
            return []

    def is_name_unique(self, name, protocol):
        return not any(c['name'].lower() == name.lower() and c['protocol'] == protocol
                       for c in self.connections)

    def save_connection(self, name, host, username, password, protocol, **kwargs):
        if not self.is_name_unique(name, protocol):
            return False, f"A {protocol} profile named '{name}' already exists."

        new_conn = {
            "name": name,
            "host": host,
            "username": username,
            "password": password,
            "protocol": protocol,
            **kwargs
        }
        self.connections.append(new_conn)
        self._write_to_file()
        self.connections_updated.emit()
        return True, "Success"

    def _write_to_file(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.connections, f, indent=4)
        except IOError as e:
            logger.error(f"Failed to write to {self.filename}: {e}")

    @staticmethod
    def test_ssh(host, port, timeout, username, password):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=timeout,
                banner_timeout=timeout,
                auth_timeout=timeout,
                allow_agent=False,
                look_for_keys=False
            )
            return True, f"Successfully authenticated via SSH at {host}:{port}"
        except paramiko.AuthenticationException:
            return False, "SSH Authentication failed: Invalid username or password."
        except Exception as e:
            return False, f"SSH connection failed: {str(e)}"
        finally:
            client.close()

    @staticmethod
    def test_telnet(host, port, timeout, password):
        """
        Performs a basic Telnet login test expecting only a password prompt.
        """
        try:
            tn = telnetlib.Telnet(host, port, timeout=timeout)
            if password:
                tn.read_until(b"Password: ", timeout=timeout)
                tn.write(password.encode('ascii') + b"\n")

            response = tn.read_until(b">", timeout=2.0)
            tn.close()

            if b"Login invalid" in response or b"Authentication failed" in response:
                return False, "Telnet Authentication failed."
            return True, f"Telnet service reached at {host}:{port}"
        except Exception as e:
            return False, f"Telnet connection failed: {str(e)}"

    @staticmethod
    def test_serial_connection(port, baud):
        try:
            test_conn = serial.Serial(port=port, baudrate=baud, timeout=0.1)
            test_conn.close()
            return True, f"Port {port} is available."
        except Exception as e:
            return False, str(e)