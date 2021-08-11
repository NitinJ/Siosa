import json
import logging

from siosa.common.singleton import Singleton
from siosa.config.metadata import get_default_config
from siosa.config.utils import validate_fields


class SiosaConfig(metaclass=Singleton):
    def __init__(self, config_json, config_file_path=None):
        super(SiosaConfig, self).__init__()
        if config_json is None:
            config_json = {}

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.config_file_path = config_file_path
        self.config_json = config_json

        self.valid_state = {}
        self._validate()
        self.logger.debug(
            "Initialized config: {}".format(str(self.config_json)))

    @staticmethod
    def create_from_file(config_file_path):
        # Config json will always have all the fields.
        config_json = get_default_config()
        try:
            config_json.update(json.load(open(config_file_path, 'r')))
        except:
            config_json.update({})
        return SiosaConfig(config_json, config_file_path)

    def _validate(self):
        self.valid_state = validate_fields(self.config_json, self.config_json)

    def get_status(self):
        return self.valid_state

    def is_valid(self):
        return all([status == 'valid' for status in self.valid_state.values()])

    def _segregate_fields(self, config_json):
        new_fields = {}
        old_fields = {}
        for field_name, field_value in config_json.items():
            if field_name in self.config_json and \
                    self.config_json[field_name] == field_value:
                # Field already present and is equal.
                old_fields[field_name] = field_value
            else:
                new_fields[field_name] = field_value
        return new_fields, old_fields

    def update(self, config_json):
        """
        Takes in a config_json object, updates the config with those keys.
        Returns status for each key.
        """
        if config_json is None:
            return None

        # Remove fields fom incoming config_json which are same as the stored
        # ones.
        new_fields, old_fields = self._segregate_fields(config_json)

        # Validate all new fields.
        valid_status_new_fields = validate_fields(new_fields, self.config_json)
        valid_status_old_fields = {k: self.valid_state[k] for k in old_fields}

        # Get only the valid new fields.
        for field_name, field_value in new_fields.items():
            if field_name in valid_status_new_fields and \
                    valid_status_new_fields[field_name] == 'valid':
                self.config_json[field_name] = field_value
                self.valid_state[field_name] = 'valid'

        if self.is_valid():
            self.logger.info(
                "Updated config: {}".format(str(self.config_json)))
            self.write_config()

        valid_status_old_fields.update(valid_status_new_fields)
        return valid_status_old_fields

    def write_config(self):
        if self.config_file_path:
            json.dump(self.config_json, open(self.config_file_path, 'w'),
                      indent=4)

    def to_json(self):
        return self.config_json

    def get_account_name(self):
        return self.config_json['account_name']

    def get_poe_session_id(self):
        return self.config_json['poe_session_id']

    def get_league(self):
        return self.config_json['league']

    def get_client_log_file_path(self):
        return self.config_json['client_log_file_path']

    def get_license_key(self):
        return self.config_json['license_key']

    def get_close_all_interfaces_shortcut(self):
        return self.config_json['close_all_user_interface']

    def get_task_stop_shortcut(self):
        return self.config_json['task_stop']

    def get_sell_tabs_names(self):
        return self.config_json['sell']

    def get_currency_stash_names(self):
        return self.config_json['currency']

    def get_dump_stash_names(self):
        return self.config_json['dump']
