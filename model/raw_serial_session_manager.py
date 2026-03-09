import threading
import time
import serial
from PySide6.QtCore import QObject, Signal


class RawSerialSessionManager(QObject):
    """
    Manages raw serial connections for low-level device interaction, bypassing strict prompt expectations.
    Designed specifically for bootloader and ROMMON environments during password recovery.
    """
    data_received = Signal(str)
    connection_lost = Signal(str)
    error_occurred = Signal(str)

    def __init__(self):
        """
        Initializes the raw serial session manager with default disconnected states.
        """
        super().__init__()
        self.connection = None
        self._receiving = False
        self._lock = threading.Lock()
        self._buffer = ""
        self._buffer_lock = threading.Lock()

    def connect_device(self, port: str, baudrate: int = 9600) -> tuple:
        """
        Establishes a raw serial connection to the specified COM port and starts the read loop.
        """
        try:
            self.connection = serial.Serial(port=port, baudrate=baudrate, timeout=0.1)
            self._receiving = True
            threading.Thread(target=self._read_loop, daemon=True).start()
            return True, "Connection successful"
        except serial.SerialException as e:
            return False, str(e)
        except Exception as e:
            return False, str(e)

    def _read_loop(self):
        """
        Continuously polls the serial port for incoming bytes, updates the internal buffer, and emits to the UI.
        """
        while self._receiving and self.connection and self.connection.is_open:
            try:
                if self.connection.in_waiting > 0:
                    raw_bytes = self.connection.read(self.connection.in_waiting)
                    if raw_bytes:
                        text = raw_bytes.decode('utf-8', errors='replace')
                        with self._buffer_lock:
                            self._buffer += text
                        self.data_received.emit(text)
                time.sleep(0.01)
            except serial.SerialException as e:
                self._handle_disconnect(f"Serial port disconnected: {str(e)}")
                break
            except Exception as e:
                self._handle_disconnect(str(e))
                break

    def write_channel(self, text: str):
        """
        Sends a raw string over the serial connection.
        """
        with self._lock:
            if self.connection and self.connection.is_open:
                try:
                    self.connection.write(text.encode('utf-8'))
                except Exception as e:
                    self.error_occurred.emit(str(e))

    def read_until_pattern(self, expected_strings: list, timeout: float = 10.0) -> str:
        """
        Blocks and reads from the internal buffer until one of the expected strings appears or the timeout is reached.
        """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            with self._buffer_lock:
                for pattern in expected_strings:
                    if pattern in self._buffer:
                        result = self._buffer
                        self._buffer = ""
                        return result
            time.sleep(0.1)

        with self._buffer_lock:
            result = self._buffer
            self._buffer = ""
        return result

    def clear_buffer(self):
        """
        Clears the internal read buffer.
        """
        with self._buffer_lock:
            self._buffer = ""

    def _handle_disconnect(self, message: str):
        """
        Cleans up the connection state and notifies the UI of a lost connection.
        """
        if self._receiving:
            self._receiving = False
            self.connection_lost.emit(message)
            self.close_connection()

    def close_connection(self):
        """
        Gracefully terminates the serial connection and background loop.
        """
        self._receiving = False
        with self._lock:
            if self.connection and self.connection.is_open:
                try:
                    self.connection.close()
                except Exception:
                    pass
            self.connection = None