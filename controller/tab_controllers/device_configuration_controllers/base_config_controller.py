class BaseConfigController:
    """
    Base controller class managing the relationship between configuration views and models.
    """

    def __init__(self, view, model):
        """
        Initializes the base controller and binds the default apply signal.
        """
        self.view = view
        self.model = model
        self._setup_connections()

    def _setup_connections(self):
        """
        Connects the view's generic apply signal to the controller's processing method.
        """
        self.view.apply_config_signal.connect(self.handle_apply)

    def handle_apply(self, data: dict):
        """
        Must be implemented by child classes to validate and pass data to the model.
        """
        raise NotImplementedError