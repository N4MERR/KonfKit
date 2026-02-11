from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QFrame, QLabel
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QTextCursor

class TerminalWidget(QWidget):
    key_pressed = Signal(str)

    def __init__(self, title="Device Terminal", parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 11pt; font-weight: bold; margin-bottom: 5px;")
        self.layout.addWidget(self.title_label)

        self.console_output = QPlainTextEdit()
        self.console_output.setFrameShape(QFrame.NoFrame)
        self.layout.addWidget(self.console_output)
        self.console_output.installEventFilter(self)

        self.set_terminal_enabled(False)

    def set_terminal_enabled(self, enabled: bool):
        self.console_output.setEnabled(enabled)
        if not enabled:
            self.console_output.setStyleSheet(
                "background-color: #0d0d0d; color: #555555; font-family: 'Consolas', monospace; font-size: 10pt; padding: 5px;"
            )
        else:
            self.console_output.setStyleSheet(
                "background-color: #1e1e1e; color: #dcdcdc; font-family: 'Consolas', monospace; font-size: 10pt; padding: 5px;"
            )

    def eventFilter(self, obj, event):
        if obj is self.console_output and event.type() == event.Type.KeyPress:
            if not self.console_output.isEnabled():
                return True

            key = event.key()
            if key == Qt.Key_Up:
                self.key_pressed.emit("KEY_UP")
                return True
            if key == Qt.Key_Down:
                self.key_pressed.emit("KEY_DOWN")
                return True
            if key == Qt.Key_Tab:
                self.key_pressed.emit("\t")
                return True
            if key == Qt.Key_Backspace:
                self.key_pressed.emit("\x08")
                return True
            if key in (Qt.Key_Return, Qt.Key_Enter):
                self.key_pressed.emit("\r")
                return True

            text = event.text()
            if text:
                self.key_pressed.emit(text)
                return True
        return super().eventFilter(obj, event)

    def append_output(self, text):
        cursor = self.console_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        if "\x08 \x08" in text or "\x08" in text:
            cursor.deletePreviousChar()
        else:
            cursor.insertText(text)
        self.console_output.setTextCursor(cursor)
        self.console_output.ensureCursorVisible()

    def append_internal_command(self, cmd):
        self.console_output.appendHtml(f"<b style='color: #4fc1ff;'>{cmd}</b>")
        self.console_output.ensureCursorVisible()