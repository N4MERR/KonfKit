import telnetlib
import threading
import time
import socket
import logging
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

class TelnetConnectionManager(QObject):
    """
    Manages Telnet communication using a polled reading mechanism to handle remote host output.
    """
    data_received = Signal(str)
    connection_lost = Signal(str)

    def __init__(self):
        super().__init__()
        self.tn = None
        self._receiving = False

    def connect_telnet(self, host, port=23, timeout=10):
        """
        Opens a Telnet connection to the target host and starts the background reception thread.
        """
        try:
            self.tn = telnetlib.Telnet(host, port, timeout)
            self._receiving = True
            threading.Thread(target=self._read_output, args=(self.tn,), daemon=True).start()
            return True, "Connection successful"
        except socket.timeout:
            return False, "Connection timed out. Host unreachable."
        except ConnectionRefusedError:
            return False, "Connection refused. Telnet service might be down."
        except Exception as e:
            return False, f"Telnet Error: {str(e)}"

    def _read_output(self, current_tn):
        """
        Performs non-blocking eager reads in a loop to capture Telnet data streams.
        """
        while self._receiving:
            try:
                data = current_tn.read_very_eager()
                if data:
                    text = data.decode('utf-8', errors='ignore')
                    self.data_received.emit(text)
                else:
                    time.sleep(0.1)
            except EOFError:
                if self._receiving:
                    self._receiving = False
                    self.connection_lost.emit("Telnet connection closed by host.")
                break
            except Exception as e:
                if self._receiving:
                    self._receiving = False
                    self.connection_lost.emit(f"Telnet connection error: {str(e)}")
                break

    def send_input(self, text):
        """
        Encodes and writes text input to the active Telnet socket.
        """
        if self.tn:
            try:
                self.tn.write(text.encode('utf-8'))
            except Exception as e:
                logger.error(f"Telnet input failed: {e}")
                self.connection_lost.emit("Failed to send input.")

    def close_connection(self):
        """
        Closes the Telnet session and terminates the background processing thread.
        """
        self._receiving = False
        if self.tn:
            try:
                self.tn.close()
            except Exception as e:
                logger.error(f"Error closing Telnet connection: {e}")
            finally:
                self.tn = None