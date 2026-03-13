import threading
import logging
import time
import io
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException, ConfigInvalidException
from PySide6.QtCore import QObject, Signal

logging.getLogger("paramiko").setLevel(logging.CRITICAL)
logging.getLogger("netmiko").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


class TerminalStream(io.BufferedIOBase):
    """
    Custom stream handler that intercepts Netmiko's session logging and routes it directly to the UI signal.
    """

    def __init__(self, signal):
        """
        Initializes the terminal stream with the target UI signal.
        """
        self.signal = signal

    def writable(self):
        """
        Indicates that the stream supports writing.
        """
        return True

    def readable(self):
        """
        Indicates that the stream does not support reading.
        """
        return False

    def write(self, b):
        """
        Decodes incoming bytes, cleans up invalid characters, and emits them to the UI.
        """
        if not b:
            return 0

        text = b if isinstance(b, str) else b.decode("utf-8", "replace")

        text = text.replace("\x00", "").replace("\ufffd", "")

        if text:
            self.signal.emit(text)
        return len(b)

    def flush(self):
        """
        Satisfies the stream interface requirement without performing any action.
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
        Initializes the session manager with default disconnected states.
        """
        super().__init__()
        self.connection = None
        self._receiving = False
        self._lock = threading.Lock()
        self.session_logger = None

    def _record_and_emit(self, data):
        """
        Emits received data through the data_received signal.
        """
        if data:
            self.data_received.emit(data)

    def connect_device(self, connection_settings):
        """
        Establishes a connection to a network device and starts the background read loop.
        """
        try:
            connection_settings.pop("keepalive", None)

            self.session_logger = TerminalStream(self.data_received)
            connection_settings["session_log"] = self.session_logger

            self.connection = ConnectHandler(**connection_settings)

            if not self.connection.check_enable_mode():
                self.connection.enable()

            self._receiving = True
            threading.Thread(target=self._read_loop, daemon=True).start()
            return True, "Connection successful"
        except NetmikoTimeoutException:
            return False, "Connection timed out."
        except NetmikoAuthenticationException:
            return False, "Authentication failed."
        except Exception as e:
            error_msg = str(e).split('\n')[0].strip()
            return False, error_msg

    def _read_loop(self):
        """
        Background loop that safely reads channel data and actively polls connection health without polluting the CLI.
        """
        last_alive_check = time.time()
        while self._receiving:
            try:
                with self._lock:
                    if not self.connection:
                        break

                    log_backup = getattr(self.connection, 'session_log', None)
                    if hasattr(self.connection, 'session_log'):
                        self.connection.session_log = None

                    current_time = time.time()
                    if current_time - last_alive_check > 3.0:
                        if hasattr(self.connection, "remote_conn") and hasattr(self.connection.remote_conn, "get_transport"):
                            try:
                                transport = self.connection.remote_conn.get_transport()
                                if transport:
                                    transport.send_ignore()
                                    if not transport.is_active():
                                        raise ConnectionError("Connection dead")
                            except (Exception, OSError, EOFError):
                                raise ConnectionError("Socket unresponsive")

                        last_alive_check = current_time

                    output = self.connection.read_channel()

                    if hasattr(self.connection, 'session_log'):
                        self.connection.session_log = log_backup

                    if output:
                        clean_output = output.replace("\x00", "").replace("\ufffd", "")
                        if clean_output:
                            self._record_and_emit(clean_output)

                time.sleep(0.01)

            except (EOFError, OSError, ConnectionError) as e:
                self._handle_disconnect(str(e))
                break
            except Exception as e:
                error_msg = str(e).split('\n')[0].strip()
                self._handle_disconnect(error_msg)
                break

    def send_raw(self, text):
        """
        Sends raw text to the device through the active connection without duplicating it in the session log.
        """
        if self.connection and self._receiving:
            try:
                with self._lock:
                    log_backup = getattr(self.connection, 'session_log', None)
                    if hasattr(self.connection, 'session_log'):
                        self.connection.session_log = None

                    self.connection.write_channel(text)

                    if hasattr(self.connection, 'session_log'):
                        self.connection.session_log = log_backup

                    return True
            except Exception as e:
                error_msg = str(e).split('\n')[0].strip()
                self.error_occurred.emit(error_msg)
                return None

    def send_command(self, cmd):
        """
        Sends a single command to the device and returns the output.
        """
        if self.connection and self._receiving:
            try:
                with self._lock:
                    return self.connection.send_command(cmd)
            except Exception as e:
                error_msg = str(e).split('\n')[0].strip()
                self.error_occurred.emit(error_msg)
                return None

    def send_command_set(self, cmds):
        """
        Starts a background thread to send a set of configuration commands.
        """
        if not self.connection or not self._receiving:
            self.batch_finished.emit()
            return

        threading.Thread(target=self._run_command_set_thread, args=(cmds,), daemon=True).start()

    def _run_command_set_thread(self, cmds):
        """
        Execution logic for sending a batch of commands in a separate thread.
        """
        try:
            with self._lock:
                alive = True
                try:
                    if hasattr(self.connection, "remote_conn") and hasattr(self.connection.remote_conn, "get_transport"):
                        transport = self.connection.remote_conn.get_transport()
                        if transport and not transport.is_active():
                            alive = False
                    else:
                        alive = True
                except Exception:
                    alive = False

                if not alive:
                    raise ConnectionError("Connection closed by remote host.")

                if self.connection.check_config_mode():
                    self.connection.exit_config_mode()

                if not self.connection.check_enable_mode():
                    self.connection.enable()

                self.connection.send_config_set(
                    config_commands=cmds,
                    error_pattern=r"% (Invalid|Incomplete|Ambiguous)"
                )

        except ConfigInvalidException:
            self.error_occurred.emit("Device rejected one or more configuration commands.")
        except Exception as e:
            error_msg = str(e).split('\n')[0].strip()
            self.error_occurred.emit(error_msg)
        finally:
            self.batch_finished.emit()

    def _handle_disconnect(self, message):
        """
        Cleans up the connection state and notifies the UI of a lost connection.
        """
        if self._receiving:
            self._receiving = False
            self.connection_lost.emit(message)
            self.close_connection()

    def close_connection(self):
        """
        Gracefully disconnects the Netmiko session and closes the session logger.
        """
        self._receiving = False
        with self._lock:
            if self.connection:
                try:
                    self.connection.disconnect()
                except Exception:
                    pass
                finally:
                    self.connection = None
            if self.session_logger:
                self.session_logger.close()