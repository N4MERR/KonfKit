import logging
import serial.tools.list_ports

logger = logging.getLogger(__name__)

class PortManager:
    """
    Manages the discovery and listing of available serial COM ports on the host system.
    """

    @staticmethod
    def list_ports() -> list:
        """
        Lists all connected serial ports.
        :return: List of connected serial ports.
        """
        ports = serial.tools.list_ports.comports()
        return ports