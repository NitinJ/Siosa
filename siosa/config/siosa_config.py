import json
import logging

from siosa.common.singleton import Singleton


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
        return SiosaConfig(json.load(open(config_file_path, 'r')), config_file_path)

    @staticmethod
    def _validate_config(config):
        # TODO: Validate here actually
        return config

    def update(self, config=None):
        if config is None:
            return

        c = self.config.copy()
        c.update(config)
        self.config = SiosaConfig._validate_config(c)
        self.logger.info("Updating config with {}".format(str(self.config)))
        self.write_config()

    def write_config(self):
        if self.config_file_path:
            json.dump(self.config, open(self.config_file_path, 'w'), indent=4)

    def to_json(self):
        return self.config

    def get_account_name(self):
        return self.config['base']['account_name']

    def get_poe_session_id(self):
        return self.config['base']['poe_session_id']

    def get_league(self):
        return self.config['base']['league']

    def get_client_log_file_path(self):
        return self.config['base']['client_log_file_path']

    def set_license_key(self, key):
        if not key:
            return
        self.config['base']['license_key'] = key
        self.write_config()

    def get_license_key(self):
        return self.config['base']['license_key']

    def get_close_all_interfaces_shortcut(self):
        return self.config['shortcuts']['close_all_user_interface']

    def get_task_stop_shortcut(self):
        return self.config['shortcuts']['task_stop']

    def get_sell_tab_index(self):
        return self.config['stashes']['sell_index']

    def get_currency_stash_names(self):
        return self.config['stashes']['currency']

    def get_dump_stash_names(self):
        return self.config['stashes']['dump']