from model.device_configuration_models.base_interface_model import BaseInterfaceModel


class HSRPModel(BaseInterfaceModel):
    """
    Model for generating Cisco IOS commands for HSRP configuration.
    """

    def generate_commands(self, **kwargs) -> list[str]:
        """
        Generates commands for creating and configuring HSRP on an interface.
        """
        commands = []

        interface = kwargs.get("interface")
        ip_address = kwargs.get("ip_address")
        subnet_mask = kwargs.get("subnet_mask")
        standby_id = kwargs.get("standby_id")
        virtual_ip = kwargs.get("virtual_ip")
        priority = kwargs.get("priority")
        preempt = kwargs.get("preempt")

        if interface:
            commands.append(f"interface {interface}")
            if ip_address and subnet_mask:
                commands.append(f" ip address {ip_address} {subnet_mask}")

            if standby_id is not None and virtual_ip:
                commands.append(f" standby {standby_id} ip {virtual_ip}")
                if priority:
                    commands.append(f" standby {standby_id} priority {priority}")
                if preempt == "Enable":
                    commands.append(f" standby {standby_id} preempt")

            commands.append(" exit")

        commands.extend(super().generate_commands(**kwargs))
        return commands