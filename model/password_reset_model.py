from utils.cisco_devices import Device, BootEnvironment


class PasswordResetModel:
    """
    Handles the hardware-level logic for resetting Cisco device passwords.
    Maintains all required interactive commands and timing sequences utilizing a raw serial connection.
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
        """
        if device.boot_environment == BootEnvironment.ROMMON:
            self._execute_rommon_recovery()
        elif device.boot_environment == BootEnvironment.SWITCH_BOOTLOADER:
            self._execute_bootloader_recovery()

        self._apply_new_configuration(device)

    def _execute_rommon_recovery(self):
        """
        Navigates the ROMMON boot sequence for ISR/ASR routers to bypass the startup config.
        """
        self.session_manager.write_channel("\r\n")
        self.session_manager.read_until_pattern([">", "rommon"], timeout=5.0)

        self.session_manager.write_channel("confreg 0x2142\r\n")
        self.session_manager.read_until_pattern([">", "rommon"], timeout=5.0)

        self.session_manager.write_channel("reset\r\n")
        self.session_manager.read_until_pattern(["initial configuration dialog", "yes/no"], timeout=120.0)

        self.session_manager.write_channel("no\r\n")
        self.session_manager.read_until_pattern([">", "RETURN"], timeout=30.0)

        self.session_manager.write_channel("\r\n")
        self.session_manager.read_until_pattern([">"], timeout=5.0)

        self.session_manager.write_channel("enable\r\n")
        self.session_manager.read_until_pattern(["#"], timeout=5.0)

        self.session_manager.write_channel("copy startup-config running-config\r\n")
        self.session_manager.read_until_pattern(["Destination filename", "?", "#"], timeout=10.0)
        self.session_manager.write_channel("\r\n")
        self.session_manager.read_until_pattern(["#"], timeout=15.0)

    def _execute_bootloader_recovery(self):
        """
        Navigates the switch: bootloader sequence for Catalyst switches to bypass the startup config.
        """
        self.session_manager.write_channel("\r\n")
        self.session_manager.read_until_pattern(["switch:"], timeout=5.0)

        self.session_manager.write_channel("flash_init\r\n")
        self.session_manager.read_until_pattern(["switch:"], timeout=30.0)

        self.session_manager.write_channel("rename flash:config.text flash:config.text.old\r\n")
        self.session_manager.read_until_pattern(["switch:"], timeout=5.0)

        self.session_manager.write_channel("boot\r\n")
        self.session_manager.read_until_pattern(["initial configuration dialog", "yes/no"], timeout=180.0)

        self.session_manager.write_channel("no\r\n")
        self.session_manager.read_until_pattern([">", "RETURN"], timeout=30.0)

        self.session_manager.write_channel("\r\n")
        self.session_manager.read_until_pattern([">"], timeout=5.0)

        self.session_manager.write_channel("enable\r\n")
        self.session_manager.read_until_pattern(["#"], timeout=5.0)

        self.session_manager.write_channel("rename flash:config.text.old flash:config.text\r\n")
        self.session_manager.read_until_pattern(["Destination filename", "?", "#"], timeout=10.0)
        self.session_manager.write_channel("\r\n")
        self.session_manager.read_until_pattern(["#"], timeout=10.0)

        self.session_manager.write_channel("copy flash:config.text running-config\r\n")
        self.session_manager.read_until_pattern(["Destination filename", "?", "#"], timeout=10.0)
        self.session_manager.write_channel("\r\n")
        self.session_manager.read_until_pattern(["#"], timeout=15.0)

    def _apply_new_configuration(self, device: Device):
        """
        Enters global configuration mode to apply password modifications and restore standard boot behavior.
        """
        self.session_manager.write_channel("configure terminal\r\n")
        self.session_manager.read_until_pattern(["(config)#"], timeout=5.0)

        if self.remove_privileged_exec_mode_password:
            self.session_manager.write_channel("no enable password\r\n")
            self.session_manager.read_until_pattern(["(config)#"], timeout=2.0)
            self.session_manager.write_channel("no enable secret\r\n")
            self.session_manager.read_until_pattern(["(config)#"], timeout=2.0)

        if self.set_new_privileged_exec_mode_password:
            mode = "secret" if self.encrypt_enable_password else "password"
            self.session_manager.write_channel(f"enable {mode} {self.new_privileged_exec_mode_password}\r\n")
            self.session_manager.read_until_pattern(["(config)#"], timeout=2.0)

        if self.remove_line_console_password or self.set_new_line_console_password:
            self.session_manager.write_channel("line console 0\r\n")
            self.session_manager.read_until_pattern(["(config-line)#"], timeout=2.0)

            if self.remove_line_console_password:
                self.session_manager.write_channel("no login\r\n")
                self.session_manager.read_until_pattern(["(config-line)#"], timeout=2.0)
                self.session_manager.write_channel("no password\r\n")
                self.session_manager.read_until_pattern(["(config-line)#"], timeout=2.0)

            if self.set_new_line_console_password:
                self.session_manager.write_channel(f"password {self.new_line_console_password}\r\n")
                self.session_manager.read_until_pattern(["(config-line)#"], timeout=2.0)
                self.session_manager.write_channel("login\r\n")
                self.session_manager.read_until_pattern(["(config-line)#"], timeout=2.0)

            self.session_manager.write_channel("exit\r\n")
            self.session_manager.read_until_pattern(["(config)#"], timeout=2.0)

        if device.boot_environment == BootEnvironment.ROMMON:
            self.session_manager.write_channel("config-register 0x2102\r\n")
            self.session_manager.read_until_pattern(["(config)#"], timeout=2.0)

        self.session_manager.write_channel("end\r\n")
        self.session_manager.read_until_pattern(["#"], timeout=5.0)

        self.session_manager.write_channel("copy running-config startup-config\r\n")
        self.session_manager.read_until_pattern(["Destination filename", "?"], timeout=10.0)
        self.session_manager.write_channel("\r\n")
        self.session_manager.read_until_pattern(["#", "OK"], timeout=15.0)

        self.session_manager.write_channel("reload\r\n")
        self.session_manager.read_until_pattern(["Proceed with reload", "yes/no", "?"], timeout=10.0)
        self.session_manager.write_channel("\r\n")
        self.session_manager.read_until_pattern(["Press RETURN to get started", "User Access Verification", "Username:", "Password:", ">", "login:"], timeout=300.0)