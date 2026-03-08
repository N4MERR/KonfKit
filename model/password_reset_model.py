# rocnikovy_projekt_new/model/password_reset_model.py
import time
from utils.cisco_devices import Device, BootEnvironment

class PasswordResetModel:
    """
    Handles the hardware-level logic for resetting Cisco device passwords.
    Maintains all required interactive commands and timing sequences.
    """

    def __init__(self):
        """
        Initializes the configuration states.
        """
        self.session_manager = None
        self.remove_privileged_exec_mode_password = False
        self.remove_line_console_password = False
        self.encrypt_enable_password = False
        self.set_new_privileged_exec_mode_password = False
        self.set_new_line_console_password = False
        self.new_privileged_exec_mode_password = ""
        self.new_line_console_password = ""

    def reset_password(self, device: Device):
        """
        Executes the full password reset workflow synchronously by fusing bypass and config tasks.
        Relies on the manager's internal lock handling.
        """
        if device.boot_environment == BootEnvironment.ROMMON:
            with self.session_manager._lock:
                conn = self.session_manager.connection
                conn.send_command_timing("\n")
                conn.send_command_timing("confreg 0x2142")
                conn.send_command_timing("reset")
                time.sleep(15)
                conn.send_command_timing("no")
                conn.send_command_timing("enable")
                conn.send_command_timing("copy startup-config running-config")
                conn.send_command_timing("\n")

        elif device.boot_environment == BootEnvironment.SWITCH_BOOTLOADER:
            with self.session_manager._lock:
                conn = self.session_manager.connection
                conn.send_command_timing("\n")
                conn.send_command_timing("flash_init")
                time.sleep(5)
                conn.send_command_timing("rename flash:config.text flash:config.text.old")
                conn.send_command_timing("boot")
                time.sleep(15)
                conn.send_command_timing("no")
                conn.send_command_timing("enable")
                conn.send_command_timing("rename flash:config.text.old flash:config.text")
                conn.send_command_timing("\n")
                conn.send_command_timing("copy flash:config.text running-config")
                conn.send_command_timing("\n")

        commands = []
        if self.remove_privileged_exec_mode_password:
            commands.extend(["no enable password", "no enable secret"])
        if self.set_new_privileged_exec_mode_password:
            mode = "secret" if self.encrypt_enable_password else "password"
            commands.append(f"enable {mode} {self.new_privileged_exec_mode_password}")
        if self.remove_line_console_password:
            commands.extend(["line console 0", "no login", "no password", "exit"])
        if self.set_new_line_console_password:
            commands.extend(["line console 0", f"password {self.new_line_console_password}", "login", "exit"])

        if device.boot_environment == BootEnvironment.ROMMON:
            commands.append("config-register 0x2102")

        if commands:
            with self.session_manager._lock:
                self.session_manager.connection.send_config_set(commands)

        with self.session_manager._lock:
            conn = self.session_manager.connection
            conn.send_command_timing("end")
            conn.send_command_timing("copy running-config startup-config")
            conn.send_command_timing("\n")
            conn.send_command_timing("reload")
            conn.send_command_timing("\n")

        self.session_manager.close_connection()