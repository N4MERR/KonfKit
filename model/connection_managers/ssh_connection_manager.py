import paramiko
import threading
import time
import logging
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class SSHConnectionManager(QObject):
    """
    Manages active SSH sessions. Handles connection establishment,
    data transmission, and reception.
    """
    data_received = Signal(str)
    connection_lost = Signal(str)

    def __init__(self):
        super().__init__()
        self.ssh_client = None
        self.shell = None
        self._receiving = False

    def connect_ssh(self, host, username, password, port=22, timeout=10):
        """
        Establishes an SSH connection to the specified host and opens an interactive shell.
        """
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(hostname=host, port=port, username=username, password=password, timeout=timeout)

            self.shell = self.ssh_client.invoke_shell()
            self.shell.setblocking(0)

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
        """
        Continuously reads data from the SSH shell and emits it via signals.
        Detects connection closure via EOF or empty bytes.
        """
        while self._receiving:
            try:
                if self.shell and (self.shell.closed or self.shell.eof_received):
                    self._receiving = False
                    self.connection_lost.emit("Connection closed by remote host.")
                    break

                if self.shell and self.shell.recv_ready():
                    data = self.shell.recv(4096)

                    if len(data) == 0:
                        self._receiving = False
                        self.connection_lost.emit("Connection closed.")
                        break

                    text = data.decode('utf-8', errors='ignore')
                    self.data_received.emit(text)
                else:
                    time.sleep(0.01)

            except Exception as e:
                self._receiving = False
                logger.error(f"Error reading SSH output: {e}")
                self.connection_lost.emit(f"Connection lost: {str(e)}")

    def send_input(self, text):
        """
        Sends data to the active SSH shell.
        """
        if self.shell:
            try:
                self.shell.send(text)
            except Exception as e:
                logger.error(f"Input transmission failed: {e}")
                self.connection_lost.emit("Failed to send input.")

    def close_connection(self):
        """
        Closes the SSH shell and client connection.
        """
        self._receiving = False
        try:
            if self.shell:
                self.shell.close()
            if self.ssh_client:
                self.ssh_client.close()
        except Exception as e:
            logger.error(f"Error closing SSH connection: {e}")