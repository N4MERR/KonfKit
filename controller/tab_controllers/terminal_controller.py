from PySide6.QtCore import QObject

class TerminalController(QObject):
    def __init__(self, terminal_widget, connection_manager):
        super().__init__()
        self.view = terminal_widget
        self.manager = connection_manager
        self.history = []
        self.history_index = -1
        self._current_line = ""
        self._connect_signals()

    def _connect_signals(self):
        self.view.key_pressed.connect(self.handle_input)
        self.manager.data_received.connect(self.view.append_output)
        # Record commands sent by automated scripts or Enter key
        if hasattr(self.manager, 'command_sent'):
            self.manager.command_sent.connect(self.record_command)

    def record_command(self, cmd):
        """Adds a sent command to the history list."""
        if not self.history or self.history[-1] != cmd:
            self.history.append(cmd)
        self.history_index = -1

    def handle_input(self, input_val):
        """Processes raw keyboard input for both Serial and SSH."""
        # Generic check: only send if the manager is ready
        # For Serial we check is_open; for SSH we check if shell exists
        is_ready = False
        if hasattr(self.manager, 'connection') and self.manager.connection:
            is_ready = self.manager.connection.is_open
        elif hasattr(self.manager, 'shell') and self.manager.shell:
            is_ready = True

        if not is_ready:
            return

        if input_val == "KEY_UP":
            if self.history and self.history_index < len(self.history) - 1:
                self.history_index += 1
                self._send_history_cmd()
        elif input_val == "KEY_DOWN":
            if self.history_index > 0:
                self.history_index -= 1
                self._send_history_cmd()
            elif self.history_index == 0:
                self.history_index = -1
                self._clear_line_on_device()
        else:
            try:
                # Use the shared .write() API
                self.manager.write(input_val.encode('utf-8'))
                if input_val == '\r':
                    self.record_command(self._current_line)
                    self._current_line = ""
                elif input_val not in ('\t', '\x08'):
                    self._current_line += input_val
            except Exception:
                pass

    def _send_history_cmd(self):
        cmd = self.history[-(self.history_index + 1)]
        self._clear_line_on_device()
        self.manager.write(cmd.encode('utf-8'))
        self._current_line = cmd

    def _clear_line_on_device(self):
        """Clears the current CLI line by sending backspaces."""
        length = len(self._current_line)
        clear_seq = b'\x08' * length + b' ' * length + b'\x08' * length
        self.manager.write(clear_seq)
        self._current_line = ""