from view.device_configuration_views.input_fields.base_input_field import BaseInputField
from view.device_configuration_views.input_fields.dropdown_field import DropdownField
from view.device_configuration_views.input_fields.password_field import PasswordField
from view.device_configuration_views.input_fields.port_combobox import PortComboBox
from .base_connection_dialog import BaseConnectionDialog


class SerialPortField(BaseInputField):
    """
    Custom input field that embeds a dynamic port selection combobox.
    """

    def _create_input_widget(self):
        """
        Instantiates the PortComboBox for serial port selection.
        """
        return PortComboBox()


class SerialConnectionDialog(BaseConnectionDialog):
    """
    Dialog for configuring a serial connection with dynamic console authentication fields.
    """

    def __init__(self, parent=None):
        """
        Initializes the serial configuration dialog.
        """
        super().__init__("Add Serial Connection", parent)

    def _add_specific_fields(self):
        """
        Injects serial parameters and the authentication mode selector.
        """
        self.port_input = SerialPortField("Serial Port:", is_optional=False)
        self.baud_input = DropdownField("Baud Rate:", ["9600", "19200", "38400", "57600", "115200"], is_optional=False)
        self.baud_input.input_widget.setCurrentText("9600")

        self.auth_mode = DropdownField("Auth Mode:", ["No Login", "Login", "Login Local"], is_optional=False)
        self.auth_mode.input_widget.currentTextChanged.connect(self._update_auth_fields)

        self.add_field(self.port_input)
        self.add_field(self.baud_input)
        self.add_field(self.auth_mode)

        self.user_input = BaseInputField("Login Username:", is_optional=False)
        self.pass_input = PasswordField("Login Password:", is_optional=False)
        self.enable_pass_input = PasswordField("Enable Password:", is_optional=True)

        self.add_field(self.user_input)
        self.add_field(self.pass_input)
        self.add_field(self.enable_pass_input)

        self._update_auth_fields()

    def _update_auth_fields(self):
        """
        Toggles visibility of credential fields based on the console authentication mode.
        """
        mode = self.auth_mode.get_value()
        self.user_input.setVisible(mode == "Login Local")
        self.pass_input.setVisible(mode in ["Login", "Login Local"])

    def get_data(self):
        """
        Extracts validated input data and maps them to serial connection parameters.
        """
        mode = self.auth_mode.get_value()
        username = self.user_input.get_value() if mode == "Login Local" else ""
        password = self.pass_input.get_value() if mode in ["Login", "Login Local"] else ""

        secret = ""
        if self.enable_pass_input.radio.isChecked():
            secret = self.enable_pass_input.get_value()

        return {
            "name": self.name_input.get_value(),
            "device_type": "cisco_ios_serial",
            "serial_settings": {
                "port": self.port_input.get_value(),
                "baudrate": int(self.baud_input.get_value())
            },
            "username": username,
            "password": password,
            "secret": secret
        }