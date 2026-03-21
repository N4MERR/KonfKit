from model.device_configuration_models.base_interface_model import BaseInterfaceModel


class HSRPModel(BaseInterfaceModel):
    """
    Model generating Cisco IOS commands for HSRP, adapting to IPv4 or IPv6 requirements natively.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates configuration commands to establish an HSRP group on a specified interface.
        """
        commands = []
        interface = kwargs.get("interface")
        group_id = kwargs.get("group_id")
        virtual_ip = kwargs.get("virtual_ip")
        version = kwargs.get("version")
        priority = kwargs.get("priority")
        preempt = kwargs.get("preempt")

        if interface and group_id and virtual_ip:
            commands.append(f"interface {interface}")

            if version == "ipv6":
                commands.append("standby version 2")
                commands.append(f"standby {group_id} ipv6 {virtual_ip}")
            else:
                commands.append(f"standby {group_id} ip {virtual_ip}")

            if priority is not None:
                commands.append(f"standby {group_id} priority {priority}")

            if preempt:
                commands.append(f"standby {group_id} preempt")

            commands.append("exit")

        commands.extend(super().generate_commands(**kwargs))
        return commands