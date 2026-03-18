from PySide6.QtCore import QThread, Signal


class ConfigApplyWorker(QThread):
    """
    Native PySide worker class to handle applying configurations asynchronously.
    """
    finished_signal = Signal(bool, str)

    def __init__(self, session_manager, commands):
        """
        Initializes the configuration application worker with session and commands.
        """
        super().__init__()
        self.session_manager = session_manager
        self.commands = commands

    def run(self):
        """
        Executes the configuration commands against the target device.
        """
        try:
            output = self.session_manager.send_command_set(self.commands)
            self.finished_signal.emit(True, output)
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class InterfaceLoadWorker(QThread):
    """
    Universal native PySide worker class to handle interface loading asynchronously.
    """
    finished_signal = Signal(list, str)

    def __init__(self, model):
        """
        Initializes the interface loading worker with the specific device model.
        """
        super().__init__()
        self.model = model

    def run(self):
        """
        Executes the interface querying logic defined in the specific model.
        """
        try:
            interfaces = self.model.get_interfaces()
            self.finished_signal.emit(interfaces if interfaces is not None else [], "")
        except Exception as e:
            self.finished_signal.emit([], str(e))


class VlanLoadWorker(QThread):
    """
    Universal native PySide worker class to handle loading VLANs asynchronously.
    """
    finished_signal = Signal(list, str)

    def __init__(self, model):
        """
        Initializes the VLAN loading worker with the specific device model.
        """
        super().__init__()
        self.model = model

    def run(self):
        """
        Executes the VLAN querying logic defined in the specific model.
        """
        try:
            vlans = self.model.get_vlans()
            self.finished_signal.emit(vlans if vlans is not None else [], "")
        except Exception as e:
            self.finished_signal.emit([], str(e))