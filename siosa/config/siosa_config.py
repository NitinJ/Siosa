import json
import logging

from siosa.common.singleton import Singleton


class SiosaConfig(metaclass=Singleton):
    def __init__(self, config_file_path):
        super(SiosaConfig, self).__init__()

        self.path = config_file_path
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Can probably use configparser or a jsonconfig parser.
        config = json.load(open(config_file_path, 'r'))
        self._validate_config(config)
        self.logger.debug("Initialized config: {}".format(str(self.config)))

    def _validate_config(self, config):
        # TODO: Validate here actually
        self.config = config

    def update(self, config={}):
        self.logger.info("Updating config with {}".format(str(config)))
        self.config.update(config)
        self._write_updated_config()

    def _write_updated_config(self):
        json.dump(self.config, open(self.path, 'w'))

    def get_sell_tab_index(self):
        return self.config['stashes']['sell_index']

    def get_account_name(self):
        return self.config['account_name']

    def get_poe_session_id(self):
        return self.config['poe_session_id']