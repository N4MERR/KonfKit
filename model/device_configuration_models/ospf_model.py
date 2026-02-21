from model.device_configuration_models.base_config_model import BaseConfigModel
from utils.response_patterns import ResponsePatterns


class OSPFModel(BaseConfigModel):
    """
    OSPF-specific configuration model inheriting from BaseConfigModel.
    """

    def generate_commands(self, process_id: str, network: str, wildcard_mask: str, area: str) -> list[str]:
        """
        Generates the sequence of OSPF configuration commands mapped directly to their execution methods.
        """
        return [
            "configure terminal",
            f"router ospf {process_id}",
            f"network {network} {wildcard_mask} area {area}"
        ]

    def apply_configuration(self, process_id: str, network: str, wildcard_mask: str, area: str):
        """
        Generates OSPF commands and sends them to the device via the session manager.
        """
        commands = self.generate_commands(process_id, network, wildcard_mask, area)
        self.session_manager.send_command_set(commands)