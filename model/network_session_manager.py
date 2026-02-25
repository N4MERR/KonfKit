"""
Manages network device sessions using Netmiko while streaming raw channel data to the UI.
"""
import threading
import logging
import time
import io
from netmiko import ConnectHandler
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

class TerminalStream(io.BufferedIOBase):
    """
    Custom stream handler that intercepts Netmiko's session logging and routes it directly to the UI signal.
    """

    def __init__(self, signal):
        """
        Initializes the stream with a target signal.
        """
        super().__init__()
        self.signal = signal

    def writable(self):
        """
        Marks the stream as writable for standard IO compatibility.
        """
        return True

    def readable(self):
        """
        Marks the stream as unreadable.
        """
        return False

    def write(self, b):
        """
        Processes incoming data and emits it as a string to the UI.
        """
        if not b:
            return 0

        text = b if isinstance(b, str) else b.decode("utf-8", "replace")

        if text:
            self.signal.emit(text)
        return len(b)

    def flush(self):
        """
        Satisfies the BufferedIOBase interface.
        """
        pass

class NetworkSessionManager(QObject):
    """
    Manages network device sessions using Netmiko while streaming raw channel data to the UI.
    """
    data_received = Signal(str)
    connection_lost = Signal(str)
    error_occurred = Signal(str)
    batch_finished = Signal()

    def __init__(self):
        """
        Initializes the session manager and state variables.
        """
        super().__init__()
        self.connection = None
        self._receiving = False
        self._lock = threading.Lock()
        self.session_logger = None

    def _record_and_emit(self, data):
        """
        Emits manual channel reads via signals to the UI.
        """
        if data:
            self.data_received.emit(data)

    def connect_device(self, connection_settings):
        """
        Establishes a device connection and configures the live terminal stream.
        """
        try:
            self.session_logger = TerminalStream(self.data_received)
            connection_settings["session_log"] = self.session_logger

            self.connection = ConnectHandler(**connection_settings)

            if not self.connection.check_enable_mode():
                self.connection.enable()

            self._receiving = True
            threading.Thread(target=self._read_loop, daemon=True).start()
            return True, "Connection successful"
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False, str(e)

    def _read_loop(self):
        """
        Background loop that safely reads channel data when blocking methods are inactive.
        """
        while self._receiving:
            try:
                with self._lock:
                    if self.connection:
                        log_backup = getattr(self.connection, 'session_log', None)
                        if hasattr(self.connection, 'session_log'):
                            self.connection.session_log = None

                        output = self.connection.read_channel()

                        if hasattr(self.connection, 'session_log'):
                            self.connection.session_log = log_backup

                        if output:
                            self._record_and_emit(output)
                    else:
                        break
                time.sleep(0.01)
            except Exception as e:
                self._handle_disconnect(str(e))
                break

    def send_raw(self, text):
        """
        Sends unparsed string data directly to the device channel.
        """
        if self.connection and self._receiving:
            try:
                with self._lock:
                    self.connection.write_channel(text)
                    return True
            except Exception as e:
                logger.error(f"Failed to send raw input: {e}")
                self.error_occurred.emit(str(e))
                return None

    def send_command(self, cmd):
        """
        Sends an operational command synchronously while yielding output to the terminal stream.
        """
        if self.connection and self._receiving:
            try:
                with self._lock:
                    return self.connection.send_command(cmd)
            except Exception as e:
                logger.error(f"Command failed: {e}")
                self.error_occurred.emit(str(e))
                return None

    def send_command_set(self, cmds):
        """
        Spawns a thread to process configuration commands synchronously.
        """
        if not self.connection or not self._receiving:
            self.batch_finished.emit()
            return

        threading.Thread(target=self._run_command_set_thread, args=(cmds,), daemon=True).start()

    def _run_command_set_thread(self, cmds):
        """
        Safely executes a set of configuration commands using the active connection lock and Netmiko state management.
        """
        try:
            with self._lock:
                if self.connection.check_config_mode():
                    self.connection.exit_config_mode()

                if not self.connection.check_enable_mode():
                    self.connection.enable()

                self.connection.send_config_set(
                    config_commands=cmds
                )
        except Exception as e:
            logger.error(f"Command set failed: {e}")
            self.error_occurred.emit(str(e))
        finally:
            self.batch_finished.emit()

    def _handle_disconnect(self, message):
        """
        Stops active reads and initiates shutdown upon connection loss.
        """
        if self._receiving:
            self._receiving = False
            self.connection_lost.emit(message)
            self.close_connection()

    def close_connection(self):
        """
        Terminates the network session and safely releases network resources.
        """
        self._receiving = False
        with self._lock:
            if self.connection:
                try:
                    self.connection.disconnect()
                except Exception as e:
                    logger.error(f"Error during disconnect: {e}")
                    self.error_occurred.emit(str(e))
                finally:
                    self.connection = None
            if self.session_logger:
                self.session_logger.close()