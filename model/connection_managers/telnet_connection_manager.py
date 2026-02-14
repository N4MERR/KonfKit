import telnetlib
import threading
import time
import logging
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

class TelnetConnectionManager(QObject):
    """
    Manages active Telnet sessions. Handles connection establishment,
    data transmission, and reception.
    """
    data_received = Signal(str)
    connection_lost = Signal(str)

    def __init__(self):
        super().__init__()
        self.tn = None
        self._receiving = False

    def connect_telnet(self, host, port=23, timeout=10):
        """
        Establishes a Telnet connection to the specified host.
        """
        try:
            self.tn = telnetlib.Telnet(host, port, timeout)
            self._receiving = True
            threading.Thread(target=self._read_output, daemon=True).start()
            return True
        except Exception as e:
            self.connection_lost.emit(f"Telnet error: {str(e)}")
            return False

    def _read_output(self):
        """
        Continuously reads data from the Telnet connection.
        """
        while self._receiving:
            try:
                data = self.tn.read_very_eager()
                if data:
                    text = data.decode('utf-8', errors='ignore')
                    self.data_received.emit(text)
                time.sleep(0.01)
            except EOFError:
                self._receiving = False
                self.connection_lost.emit("Telnet connection closed by host.")
            except Exception as e:
                self._receiving = False
                self.connection_lost.emit(f"Telnet connection error: {str(e)}")

    def send_input(self, text):
        """
        Sends data to the active Telnet session.
        """
        if self.tn:
            try:
                self.tn.write(text.encode('utf-8'))
            except Exception as e:
                logger.error(f"Telnet input failed: {e}")
                self.connection_lost.emit("Failed to send input.")

    def close_connection(self):
        """
        Closes the Telnet connection.
        """
        self._receiving = False
        if self.tn:
            try:
                self.tn.close()
            except Exception as e:
                logger.error(f"Error closing Telnet connection: {e}")