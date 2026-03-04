from controller.tab_controllers.device_configuration_controllers.base_table_config_controller import BaseTableConfigController

class DHCPController(BaseTableConfigController):
    """
    Dedicated controller for DHCP configurations with explicit method handlers for each action.
    """

    def _setup_connections(self):
        """
        Connects granular DHCP view signals to dedicated handler methods.
        """
        super()._setup_connections()

        self.view.apply_pool_signal.connect(self.handle_apply_pool)
        self.view.delete_pool_signal.connect(self.handle_delete_pool)
        self.view.apply_exclusion_signal.connect(self.handle_apply_exclusion)
        self.view.delete_exclusion_signal.connect(self.handle_delete_exclusion)

    def handle_apply_pool(self, data: dict):
        """
        Generates and sends commands to create or update a DHCP pool.
        """
        write_memory = data.pop("_write_memory", False)
        commands = self.model.generate_pool_commands(data)

        if write_memory:
            commands.append("do write memory")

        self._show_progress("Applying DHCP Pool...")
        self.model.session_manager.send_command_set(commands)

    def handle_delete_pool(self, data: dict):
        """
        Generates and sends commands to remove a DHCP pool.
        """
        write_memory = data.pop("_write_memory", False)
        commands = self.model.generate_delete_pool_commands(data)

        if write_memory:
            commands.append("do write memory")

        self._show_progress("Deleting DHCP Pool...")
        self.model.session_manager.send_command_set(commands)

    def handle_apply_exclusion(self, data: dict):
        """
        Generates and sends commands to configure excluded IP addresses.
        """
        write_memory = data.pop("_write_memory", False)
        commands = self.model.generate_exclusion_commands(data)

        if write_memory:
            commands.append("do write memory")

        self._show_progress("Applying Excluded Address...")
        self.model.session_manager.send_command_set(commands)

    def handle_delete_exclusion(self, data: dict):
        """
        Generates and sends commands to remove an excluded address range.
        """
        write_memory = data.pop("_write_memory", False)
        commands = self.model.generate_delete_exclusion_commands(data)

        if write_memory:
            commands.append("do write memory")

        self._show_progress("Deleting Excluded Address...")
        self.model.session_manager.send_command_set(commands)