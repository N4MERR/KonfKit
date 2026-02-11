import time
import serial
from PySide6.QtCore import QObject, Signal
from serial import SerialException
from utils.exceptions import ConnectionError

class SerialConnectionManager(QObject):
    data_received = Signal(str)
    command_sent = Signal(str)
    connection_lost = Signal(str)

    def __init__(self):
        super().__init__()
        self.connection = None
        self.port = None
        self.baud_rate = None

    def open_serial_connection(self):
        """Opens the serial port or raises ConnectionError."""
        try:
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=0.05
            )
        except SerialException as e:
            raise ConnectionError(f"Could not open port: {str(e)}")

    def close_connection(self):
        """Safely closes the active serial connection."""
        if self.connection and self.connection.is_open:
            self.connection.close()

    def write(self, data):
        """Unified write API to match SSH connection manager."""
        if self.connection and self.connection.is_open:
            self.connection.write(data)

    def send_command(self, command, response_pattern=None, timeout=2):
        """Sends a CLI command and waits for a response pattern."""
        if not self.connection or not self.connection.is_open:
            return
        try:
            if command:
                self.command_sent.emit(command)
                self.write((command + '\n').encode('utf-8'))
            if response_pattern:
                self._wait_for_response(response_pattern, timeout)
        except SerialException as e:
            self.connection_lost.emit(str(e))
            self.close_connection()

    def _wait_for_response(self, pattern, timeout):
        """Internal worker to poll the connection for a specific response."""
        end_time = time.time() + timeout
        buffer = ""
        while time.time() < end_time:
            try:
                if self.connection.in_waiting > 0:
                    chunk = self.connection.read(self.connection.in_waiting).decode('utf-8', errors='ignore')
                    buffer += chunk
                    self.data_received.emit(chunk)
                    if pattern in buffer:
                        return
                time.sleep(0.02)
            except SerialException as e:
                self.connection_lost.emit(str(e))
                return