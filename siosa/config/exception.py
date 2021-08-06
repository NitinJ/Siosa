class InvalidConfigException(Exception):
    def __init__(self, config_errors=None):
        super().__init__()
        if config_errors is None:
            config_errors = {}
        self.config_errors = config_errors