"""
Provides the interactive terminal UI component.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QFrame
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QTextCursor


class TerminalView(QWidget):
    """
    Terminal UI component providing interactive console output and keyboard capturing with a visible text cursor.
    """
    user_input_received = Signal(str)

    def __init__(self, parent=None):
        """
        Initializes the terminal layout and interactive text area.
        """
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)

        self.console_output = QPlainTextEdit()
        self.console_output.setFrameShape(QFrame.NoFrame)
        self.console_output.setReadOnly(True)

        self.console_output.setCursorWidth(2)
        self.console_output.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByKeyboard |
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.console_output.setFocusPolicy(Qt.StrongFocus)

        self.layout.addWidget(self.console_output)
        self.console_output.installEventFilter(self)

        self._protection_point = 0
        self._input_buffer = ""
        self.apply_style(False)

    def apply_style(self, enabled: bool):
        """
        Updates terminal colors based on the active connection state.
        """
        if not enabled:
            self.console_output.setStyleSheet(
                "background-color: #0d0d0d; color: #555555; font-family: 'Consolas', monospace; font-size: 10pt; padding: 5px;"
            )
        else:
            self.console_output.setStyleSheet(
                "background-color: #1e1e1e; color: #dcdcdc; font-family: 'Consolas', monospace; font-size: 10pt; padding: 5px;"
            )

    def eventFilter(self, obj, event):
        """
        Intercepts key presses and mouse clicks for redirection to the controller and cursor management.
        """
        if obj is self.console_output:
            if event.type() == event.Type.MouseButtonPress:
                res = super().eventFilter(obj, event)
                cursor = self.console_output.textCursor()
                if cursor.position() < self._protection_point:
                    cursor.setPosition(self._protection_point)
                    self.console_output.setTextCursor(cursor)
                return res

            if event.type() == event.Type.KeyPress:
                key = event.key()
                text = event.text()
                modifiers = event.modifiers()
                cursor = self.console_output.textCursor()

                if key == Qt.Key_C and (modifiers & Qt.ControlModifier):
                    self.user_input_received.emit("\x03")
                    return True

                if key == Qt.Key_Up:
                    self.user_input_received.emit("\x1b[A")
                    return True
                elif key == Qt.Key_Down:
                    self.user_input_received.emit("\x1b[B")
                    return True
                elif key == Qt.Key_Tab:
                    self.user_input_received.emit("\t")
                    return True

                if key == Qt.Key_Left:
                    self.user_input_received.emit("\x1b[D")
                    return True

                if key == Qt.Key_Right:
                    self.user_input_received.emit("\x1b[C")
                    return True

                if key in (Qt.Key_Return, Qt.Key_Enter):
                    self.user_input_received.emit("\r")
                    return True

                elif key == Qt.Key_Backspace:
                    self.user_input_received.emit("\x08")
                    return True

                elif text and key not in (Qt.Key_Escape,):
                    self.user_input_received.emit(text)
                    return True

                return True
        return super().eventFilter(obj, event)

    def display_text(self, text):
        """
        Writes received characters to the terminal buffer and updates input tracking.
        """
        cursor = self.console_output.textCursor()
        cursor.movePosition(QTextCursor.End)

        filtered_text = text.replace("\r\n", "\n").replace("\r", "")

        if "\x08" in filtered_text:
            for char in filtered_text:
                if char == "\x08":
                    if cursor.position() > 0:
                        cursor.deletePreviousChar()
                else:
                    cursor.insertText(char)
        else:
            cursor.insertText(filtered_text)

        self._protection_point = cursor.position()
        self.console_output.setTextCursor(cursor)
        self.console_output.ensureCursorVisible()

    def display_system_message(self, message):
        """
        Displays system status messages with specific formatting and a trailing newline.
        """
        cursor = self.console_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.console_output.appendHtml(f"<b style='color: #4fc1ff;'>{message}</b>")
        cursor.movePosition(QTextCursor.End)
        cursor.insertText("\n")
        self._protection_point = self.console_output.textCursor().position()
        self.console_output.setTextCursor(cursor)
        self.console_output.ensureCursorVisible()

    def clear_screen(self):
        """
        Resets the terminal display buffer.
        """
        self.console_output.clear()
        self._protection_point = 0