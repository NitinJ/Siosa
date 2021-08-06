import json
import logging

from siosa.common.singleton import Singleton
from siosa.config.exception import InvalidConfigException

from siosa.config.utils import validate_config, get_validator_for_field


class SiosaConfig(metaclass=Singleton):
    def __init__(self, config, config_file_path=None):
        super(SiosaConfig, self).__init__()
        if config is None:
            config = {}

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.config_file_path = config_file_path
        self.config = SiosaConfig._validate_config(config)
        self.logger.debug("Initialized config: {}".format(str(self.config)))

    @staticmethod
    def create_from_file(config_file_path):
        return SiosaConfig(
            json.load(open(config_file_path, 'r')), config_file_path)

    @staticmethod
    def _validate_config(config):
        """
        Validates the given config. Raises InvalidConfigException if config is
        invalid. Otherwise returns the cleaned up config object.
        Args:
            config: The config json object

        Returns: The cleaned up config json object

        """
        valid, error = validate_config(config)
        if not valid:
            raise InvalidConfigException(error)
        return config

    def update(self, config=None):
        if config is None:
            return

        c = self.config.copy()
        c.update(config)

        valid = True
        for key, value in config.items():
            if not get_validator_for_field(key)(value, c):
                self.logger.debug("Validation failed for field: {}".format(key))
                valid = False
                break

        if valid:
            self.config = c
            self.logger.info("Updating config with {}".format(
                str(self.config)))
            self.write_config()

    def write_config(self):
        if self.config_file_path:
            json.dump(self.config, open(self.config_file_path, 'w'), indent=4)

    def to_json(self):
        return self.config

    def get_account_name(self):
        return self.config['account_name']

    def get_poe_session_id(self):
        return self.config['poe_session_id']

    def get_league(self):
        return self.config['league']

    def get_client_log_file_path(self):
        return self.config['client_log_file_path']

    def get_license_key(self):
        return self.config['license_key']

    def get_close_all_interfaces_shortcut(self):
        return self.config['close_all_user_interface']

    def get_task_stop_shortcut(self):
        return self.config['task_stop']

    def get_sell_tabs_names(self):
        return self.config['sell']

    def get_currency_stash_names(self):
        return self.config['currency']

    def get_dump_stash_names(self):
        return self.config['dump']
