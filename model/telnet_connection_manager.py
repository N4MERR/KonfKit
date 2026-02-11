import telnetlib
import threading
import time
import logging
from PySide6.QtCore import QObject, Signal
from utils.exceptions import ConnectionError

logger = logging.getLogger(__name__)

class TelnetConnectionManager(QObject):
    """
    Manages Telnet connections and interactive shell sessions.
    """
    data_received = Signal(str)
    connection_lost = Signal(str)

    def __init__(self):
        super().__init__()
        self.tn = None
        self._receiving = False

    def connect_telnet(self, host, port=23, timeout=10):
        try:
            self.tn = telnetlib.Telnet(host, port, timeout)
            self._receiving = True
            threading.Thread(target=self._read_output, daemon=True).start()
            return True
        except Exception as e:
            self.connection_lost.emit(f"Telnet error: {str(e)}")
            return False

    def _read_output(self):
        while self._receiving:
            try:
                data = self.tn.read_very_eager().decode('utf-8', errors='ignore')
                if data:
                    self.data_received.emit(data)
                time.sleep(0.01)
            except Exception:
                self._receiving = False
                self.connection_lost.emit("Telnet connection lost.")

    def send_input(self, text):
        if self.tn:
            try:
                self.tn.write(text.encode('utf-8'))
            except Exception as e:
                logger.error(f"Telnet input failed: {e}")

    def close_connection(self):
        self._receiving = False
        if self.tn:
            self.tn.close()