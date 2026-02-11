import logging
from utils.cisco_devices import Device, BootEnvironment
from utils.configuration_commands import Commands, ROMMONCommands, SwitchBootloaderCommands
from utils.response_patterns import ResponsePatterns
from utils.exceptions import IncorrectResponseException, DeviceTimeoutError

logger = logging.getLogger(__name__)

class PasswordResetter:
    """
    Handles the logic for resetting Cisco device passwords.
    Uses the Command Pattern to manage individual configuration tasks.
    """
    def __init__(self):
        self.remove_privileged_exec_mode_password = False
        self.remove_line_console_password = False
        self.encrypt_enable_password = False
        self.set_new_privileged_exec_mode_password = False
        self.set_new_line_console_password = False
        self.new_privileged_exec_mode_password = ""
        self.new_line_console_password = ""
        self._execution_plan = []

    def _build_execution_plan(self):
        """Assembles the task list based on user selections."""
        self._execution_plan = []
        if self.remove_privileged_exec_mode_password:
            self._execution_plan.append(self._task_remove_enable)
        if self.set_new_privileged_exec_mode_password:
            self._execution_plan.append(self._task_set_new_enable)
        if self.remove_line_console_password:
            self._execution_plan.append(self._task_remove_console)
        if self.set_new_line_console_password:
            self._execution_plan.append(self._task_set_new_console)

    def reset_password(self, serial_manager, device: Device):
        """Executes the full password reset workflow."""
        self.ignore_startup_config(serial_manager, device)
        self._build_execution_plan()

        response = serial_manager.send_command(Commands.enter_global_configuration_mode,
                                               ResponsePatterns.GLOBAL_CONFIGURATION_MODE)
        if not response:
            raise IncorrectResponseException("Failed to enter Global Configuration mode.")

        for task in self._execution_plan:
            task(serial_manager)

        self.finish_reset(serial_manager, device)
        self._save_and_reload(serial_manager)

    def _task_remove_enable(self, serial_manager):
        """Removes existing enable passwords."""
        serial_manager.send_command(Commands.remove_enable_password, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)
        serial_manager.send_command(Commands.remove_enable_secret_password, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)

    def _task_set_new_enable(self, serial_manager):
        """Sets a new enable password or secret."""
        cmd = Commands.set_enable_secret_password if self.encrypt_enable_password else Commands.set_enable_password
        serial_manager.send_command(cmd.format(password=self.new_privileged_exec_mode_password),
                                    ResponsePatterns.GLOBAL_CONFIGURATION_MODE)

    def _task_remove_console(self, serial_manager):
        """Removes console line authentication."""
        serial_manager.send_command(Commands.enter_line_console, ResponsePatterns.LINE_CONFIGURATION_MODE)
        serial_manager.send_command(Commands.disable_login, ResponsePatterns.LINE_CONFIGURATION_MODE)
        serial_manager.send_command(Commands.remove_line_console_password, ResponsePatterns.LINE_CONFIGURATION_MODE)
        serial_manager.send_command(Commands.exit, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)

    def _task_set_new_console(self, serial_manager):
        """Sets a new console line password."""
        serial_manager.send_command(Commands.enter_line_console, ResponsePatterns.LINE_CONFIGURATION_MODE)
        serial_manager.send_command(Commands.set_line_console_password.format(password=self.new_line_console_password),
                                    ResponsePatterns.LINE_CONFIGURATION_MODE)
        serial_manager.send_command(Commands.enable_login, ResponsePatterns.LINE_CONFIGURATION_MODE)
        serial_manager.send_command(Commands.exit, ResponsePatterns.GLOBAL_CONFIGURATION_MODE)

    def ignore_startup_config(self, serial_manager, device: Device):
        """Bypasses the startup configuration based on the boot environment."""
        if device.boot_environment == BootEnvironment.ROMMON:
            self._handle_rommon_bypass(serial_manager)
        elif device.boot_environment == BootEnvironment.SWITCH_BOOTLOADER:
            self._handle_switch_bypass(serial_manager)

    def _handle_rommon_bypass(self, serial_manager):
        """Bypasses configuration for ROMMON based devices."""
        if not serial_manager.send_command(None, ResponsePatterns.ROMMON):
            raise DeviceTimeoutError("Device did not enter ROMMON.")
        serial_manager.send_command(ROMMONCommands.ignore_startup_config, ResponsePatterns.ROMMON)
        serial_manager.send_command(ROMMONCommands.reload, ResponsePatterns.INITIAL_SETUP_MESSAGE, 10)
        serial_manager.send_command(Commands.no, ResponsePatterns.EXEC_MODE)
        serial_manager.send_command(Commands.enable, ResponsePatterns.PRIVILEGED_EXEC_MODE)
        serial_manager.send_command(Commands.copy_startup_config_to_running_config,
                                    ResponsePatterns.DESTINATION_FILE_RENAME)
        serial_manager.send_command(None, ResponsePatterns.PRIVILEGED_EXEC_MODE, 10)

    def _handle_switch_bypass(self, serial_manager):
        """Bypasses configuration for Switch Bootloader based devices."""
        if not serial_manager.send_command(None, ResponsePatterns.BOOTLOADER):
            raise DeviceTimeoutError("Device did not enter Bootloader.")
        serial_manager.send_command(SwitchBootloaderCommands.initialize_flash, ResponsePatterns.BOOTLOADER)
        serial_manager.send_command(SwitchBootloaderCommands.rename_startup_config, ResponsePatterns.BOOTLOADER)
        serial_manager.send_command(SwitchBootloaderCommands.boot, ResponsePatterns.EXEC_MODE, 10)
        serial_manager.send_command(Commands.no, ResponsePatterns.EXEC_MODE)
        serial_manager.send_command(Commands.enable, ResponsePatterns.PRIVILEGED_EXEC_MODE)
        serial_manager.send_command(Commands.rename_startup_config_to_default, ResponsePatterns.DESTINATION_FILE_RENAME)
        serial_manager.send_command(None, ResponsePatterns.PRIVILEGED_EXEC_MODE)
        serial_manager.send_command(Commands.copy_config_file_to_running_config,
                                    ResponsePatterns.DESTINATION_FILE_RENAME)
        serial_manager.send_command(None, ResponsePatterns.PRIVILEGED_EXEC_MODE, 10)

    def finish_reset(self, serial_manager, device: Device):
        """Performs cleanup tasks after password configuration."""
        if device.boot_environment == BootEnvironment.ROMMON:
            serial_manager.send_command(Commands.reset_config_register_to_default,
                                        ResponsePatterns.GLOBAL_CONFIGURATION_MODE)

    def _save_and_reload(self, serial_manager):
        """Saves the running configuration and reloads the device."""
        serial_manager.send_command(Commands.end, None)
        serial_manager.send_command(None, ResponsePatterns.PRIVILEGED_EXEC_MODE)
        serial_manager.send_command(Commands.copy_running_config_to_startup_config,
                                    ResponsePatterns.DESTINATION_FILE_RENAME)
        serial_manager.send_command(None, ResponsePatterns.PRIVILEGED_EXEC_MODE)
        serial_manager.send_command(Commands.reload, ResponsePatterns.PROCEED_WITH_RELOAD)
        serial_manager.close_connection()