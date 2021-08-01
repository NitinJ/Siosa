from siosa.config.siosa_config import SiosaConfig


class ConfigService:
    def __init__(self, siosa_config: SiosaConfig, config_file_path):
        self.config = siosa_config
        self.config_file_path = config_file_path

    def update(self, config):
        self.config.update(config)
        return self.config.to_json()

    def get(self):
        return self.config.to_json()
