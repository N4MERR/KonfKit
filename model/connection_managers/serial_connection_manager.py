import serial
import threading
import time
import logging
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

class SerialConnectionManager(QObject):
    """
    Manages active Serial connections. Handles port opening,
    data transmission, and reception.
    """
    data_received = Signal(str)
    connection_lost = Signal(str)

    def __init__(self):
        super().__init__()
        self.serial_conn = None
        self._receiving = False

    def connect_serial(self, port, baudrate=9600, timeout=1):
        """
        Opens a serial connection to the specified port and baudrate.
        """
        try:
            self.serial_conn = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
            self._receiving = True
            threading.Thread(target=self._read_output, daemon=True).start()
            return True
        except serial.SerialException as e:
            self.connection_lost.emit(f"Serial error: {str(e)}")
            return False

    def _read_output(self):
        """
        Continuously reads data from the Serial port.
        """
        while self._receiving:
            try:
                if self.serial_conn and self.serial_conn.is_open and self.serial_conn.in_waiting > 0:
                    data = self.serial_conn.read(self.serial_conn.in_waiting)
                    text = data.decode('utf-8', errors='ignore')
                    self.data_received.emit(text)
                time.sleep(0.01)
            except serial.SerialException as e:
                self._receiving = False
                self.connection_lost.emit(f"Serial connection lost: {str(e)}")
            except Exception as e:
                self._receiving = False
                self.connection_lost.emit(f"Error reading serial: {str(e)}")

    def send_input(self, text):
        """
        Sends data to the active serial connection.
        """
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(text.encode('utf-8'))
            except Exception as e:
                logger.error(f"Serial input failed: {e}")
                self.connection_lost.emit("Failed to send input.")

    def close_connection(self):
        """
        Closes the Serial connection.
        """
        self._receiving = False
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
            except Exception as e:
                logger.error(f"Error closing serial connection: {e}")