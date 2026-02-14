import threading
import logging
import time
from netmiko import ConnectHandler
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

class NetworkSessionManager(QObject):
    """
    Core engine for managing multi-protocol network sessions and batch command execution.
    """
    data_received = Signal(str)
    connection_lost = Signal(str)

    def __init__(self):
        super().__init__()
        self.connection = None
        self._receiving = False

    def connect_device(self, connection_settings):
        """
        Establishes a connection by passing settings directly to the handler.
        """
        try:
            self.connection = ConnectHandler(**connection_settings)
            self._receiving = True
            threading.Thread(target=self._read_loop, daemon=True).start()
            return True, "Connection successful"
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False, str(e)

    def _read_loop(self):
        """
        Continuously polls the session for new data and emits it to the UI.
        """
        while self._receiving:
            try:
                if self.connection and self.connection.is_alive():
                    output = self.connection.read_channel()
                    if output:
                        self.data_received.emit(output)
                    else:
                        time.sleep(0.05)
                else:
                    self._handle_disconnect("Connection lost.")
                    break
            except Exception as e:
                self._handle_disconnect(f"Read error: {str(e)}")
                break

    def send_raw(self, text):
        """
        Sends raw characters for interactive terminal use and echoes to UI.
        """
        if self.connection and self._receiving:
            try:
                self.connection.write_channel(text)
                self.data_received.emit(text)
            except Exception as e:
                logger.error(f"Failed to send raw input: {e}")

    def send_exec_command(self, cmd):
        """
        Sends a single command in Privilege EXEC mode (#).
        """
        if self.connection and self._receiving:
            try:
                if not self.connection.check_enable_mode():
                    self.connection.enable()
                self.data_received.emit(f"{cmd}\n")
                result = self.connection.send_command(cmd)
                self.data_received.emit(f"{result}\n")
                return result
            except Exception as e:
                logger.error(f"EXEC command failed: {e}")
                return None

    def send_config_command(self, cmd):
        """
        Enters Global Config mode, executes a single command, and exits.
        """
        if self.connection and self._receiving:
            try:
                self.data_received.emit(f"{cmd} (config)\n")
                result = self.connection.send_config_set([cmd])
                self.data_received.emit(f"{result}\n")
                return result
            except Exception as e:
                logger.error(f"Config command failed: {e}")
                return None

    def send_rommon_command(self, cmd, prompt=r">"):
        """
        Sends a single command in ROMmon or bootloader mode.
        """
        if self.connection and self._receiving:
            try:
                self.data_received.emit(f"{cmd}\n")
                result = self.connection.send_command(cmd, expect_string=prompt)
                self.data_received.emit(f"{result}\n")
                return result
            except Exception as e:
                logger.error(f"ROMmon command failed: {e}")
                return None

    def send_and_expect(self, cmd_data):
        """
        Sends a command and waits for a specific string pattern.
        """
        if self.connection and self._receiving:
            cmd, pattern = cmd_data
            try:
                self.data_received.emit(f"{cmd}\n")
                result = self.connection.send_command(cmd, expect_string=pattern)
                self.data_received.emit(f"{result}\n")
                return result
            except Exception as e:
                logger.error(f"Send and expect failed: {e}")
                return None

    def execute_batch(self, command_list):
        """
        Executes a list of tuples containing (method_reference, argument).
        """
        if not self.connection or not self._receiving:
            return

        def _run_batch():
            for method, arg in command_list:
                try:
                    method(arg)
                except Exception as e:
                    logger.error(f"Batch execution step failed: {e}")

        threading.Thread(target=_run_batch, daemon=True).start()

    def _handle_disconnect(self, message):
        """
        Internal cleanup when a connection is lost or closed.
        """
        if self._receiving:
            self._receiving = False
            self.connection_lost.emit(message)
            self.close_connection()

    def close_connection(self):
        """
        Disconnects the session and releases resources.
        """
        self._receiving = False
        if self.connection:
            try:
                self.connection.disconnect()
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
            finally:
                self.connection = None