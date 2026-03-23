from PySide6.QtCore import QThread, Signal


def _ensure_enable_mode(session_manager):
    """
    Safely transitions the network device to privileged EXEC mode if it is not already.
    Exits configuration mode prior to checking the enable state to prevent command failures.
    """
    if not session_manager or getattr(session_manager, "connection", None) is None:
        return

    try:
        with session_manager._lock:
            if session_manager.connection.check_config_mode():
                session_manager.connection.exit_config_mode()

            if not session_manager.connection.check_enable_mode():
                session_manager.connection.enable()
    except Exception:
        pass


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
            _ensure_enable_mode(self.model.session_manager)
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
            _ensure_enable_mode(self.model.session_manager)
            vlans = self.model.get_vlans()
            self.finished_signal.emit(vlans if vlans is not None else [], "")
        except Exception as e:
            self.finished_signal.emit([], str(e))


class ACLLoadWorker(QThread):
    """
    Native PySide worker class to handle loading Access Control Lists asynchronously.
    """
    finished_signal = Signal(list, str)

    def __init__(self, model):
        """
        Initializes the ACL loading worker with the specific device model.
        """
        super().__init__()
        self.model = model

    def run(self):
        """
        Executes the ACL querying logic defined in the specific model.
        """
        try:
            _ensure_enable_mode(self.model.session_manager)
            acls = self.model.get_acls()
            self.finished_signal.emit(acls if acls is not None else [], "")
        except Exception as e:
            self.finished_signal.emit([], str(e))


class PoolLoadWorker(QThread):
    """
    Native PySide worker class to handle loading NAT Pools asynchronously.
    """
    finished_signal = Signal(list, str)

    def __init__(self, model):
        """
        Initializes the NAT pool loading worker with the specific device model.
        """
        super().__init__()
        self.model = model

    def run(self):
        """
        Executes the NAT pool querying logic defined in the specific model.
        """
        try:
            _ensure_enable_mode(self.model.session_manager)
            pools = self.model.get_pools()
            self.finished_signal.emit(pools if pools is not None else [], "")
        except Exception as e:
            self.finished_signal.emit([], str(e))


class NatLoadWorker(QThread):
    """
    Asynchronous worker for fetching NAT-specific device data (ACLs and Pools).
    """
    finished_signal = Signal(str, list)

    def __init__(self, model, data_type):
        """
        Initializes the worker with the model and the specific data category to fetch.
        """
        super().__init__()
        self.model = model
        self.data_type = data_type

    def run(self):
        """
        Executes retrieval logic and ensures signals are emitted even on failure.
        """
        try:
            _ensure_enable_mode(self.model.session_manager)
            data = []
            if self.data_type == "acls":
                data = self.model.get_acls()
            elif self.data_type == "pools":
                data = self.model.get_pools()

            self.finished_signal.emit(self.data_type, data if data is not None else [])
        except Exception:
            self.finished_signal.emit(self.data_type, [])