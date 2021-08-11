from siosa.config.siosa_config import SiosaConfig


class ConfigService:
    def __init__(self, siosa_config: SiosaConfig, config_file_path):
        self.config = siosa_config
        self.config_file_path = config_file_path

    def update(self, config):
        error = self.config.update(config)
        return {
            "config": self.config.to_json(),
            "error": error,
            "valid": self.config.is_valid()
        }

    def get(self):
        return {
            "config": self.config.to_json(),
            "valid": self.config.is_valid(),
            "status": self.config.get_status()
        }
