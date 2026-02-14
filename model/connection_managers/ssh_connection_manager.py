import paramiko
import threading
import socket
import logging
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class SSHConnectionManager(QObject):
    """
    Manages the lifecycle of an SSH session, providing thread-safe data reception and transmission.
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
        Establishes an SSH connection and initializes an interactive shell with blocking reads.
        """
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=timeout,
                allow_agent=False,
                look_for_keys=False
            )

            self.shell = self.ssh_client.invoke_shell()
            self.shell.setblocking(1)

            self._receiving = True
            threading.Thread(target=self._read_output, args=(self.shell,), daemon=True).start()
            return True, "Connection successful"

        except paramiko.AuthenticationException:
            return False, "Authentication failed: Invalid username or password."
        except socket.timeout:
            return False, "Connection timed out."
        except Exception as e:
            return False, str(e)

    def _read_output(self, current_shell):
        """
        Internal loop for receiving data. Uses blocking recv to prevent premature thread exit.
        """
        while self._receiving:
            try:
                data = current_shell.recv(4096)

                if not data:
                    if self._receiving:
                        self._receiving = False
                        self.connection_lost.emit("Remote host closed the connection.")
                    break

                text = data.decode('utf-8', errors='ignore')
                self.data_received.emit(text)

            except (socket.error, Exception) as e:
                if self._receiving:
                    self._receiving = False
                    self.connection_lost.emit(f"Connection error: {str(e)}")
                break

    def send_input(self, text):
        """
        Transmits text to the remote shell.
        """
        if self.shell and not self.shell.closed:
            try:
                self.shell.send(text)
            except Exception as e:
                logger.error(f"Failed to send input: {e}")

    def close_connection(self):
        """
        Stops the reception loop and releases SSH resources.
        """
        self._receiving = False
        try:
            if self.shell:
                self.shell.close()
            if self.ssh_client:
                self.ssh_client.close()
        except Exception as e:
            logger.error(f"Error during SSH shutdown: {e}")
        finally:
            self.shell = None
            self.ssh_client = None