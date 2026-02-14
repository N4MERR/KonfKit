import serial
import threading
import time
import logging
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

class SerialConnectionManager(QObject):
    """
    Manages hardware serial port communication including port initialization and data throughput.
    """
    data_received = Signal(str)
    connection_lost = Signal(str)

    def __init__(self):
        super().__init__()
        self.serial_conn = None
        self._receiving = False

    def connect_serial(self, port, baudrate=9600, timeout=0.1):
        """
        Initializes the serial port with specified parameters and starts the data monitoring thread.
        """
        try:
            self.serial_conn = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
            self._receiving = True
            threading.Thread(target=self._read_output, args=(self.serial_conn,), daemon=True).start()
            return True, "Connection successful"
        except serial.SerialException as e:
            if "Access is denied" in str(e):
                return False, f"Access denied. Port {port} might be in use."
            elif "FileNotFoundError" in str(e) or "The system cannot find" in str(e):
                return False, f"Port {port} not found. Check cable."
            return False, f"Serial Error: {str(e)}"
        except ValueError:
            return False, "Invalid parameters (e.g., baudrate)."
        except Exception as e:
            return False, f"Error: {str(e)}"

    def _read_output(self, current_serial):
        """
        Monitors the serial buffer and emits received data as string sequences.
        """
        while self._receiving:
            try:
                if current_serial.is_open:
                    data = current_serial.read(1024)
                    if data:
                        text = data.decode('utf-8', errors='ignore')
                        self.data_received.emit(text)
                else:
                    if self._receiving:
                        self._receiving = False
                        self.connection_lost.emit("Serial port closed unexpectedly.")
                    break
            except serial.SerialException as e:
                if self._receiving:
                    self._receiving = False
                    self.connection_lost.emit(f"Serial connection lost: {str(e)}")
                break
            except Exception as e:
                if self._receiving:
                    self._receiving = False
                    self.connection_lost.emit(f"Error reading serial: {str(e)}")
                break

    def send_input(self, text):
        """
        Writes raw byte sequences to the serial hardware interface.
        """
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(text.encode('utf-8'))
            except Exception as e:
                logger.error(f"Serial input failed: {e}")
                self.connection_lost.emit("Failed to send input.")

    def close_connection(self):
        """
        Releases the serial port and stops the reception thread.
        """
        self._receiving = False
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
            except Exception as e:
                logger.error(f"Error closing serial connection: {e}")
            finally:
                self.serial_conn = None