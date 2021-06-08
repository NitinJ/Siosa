import json
import logging
from pprint import pformat

from tools.roller.crafting_type import get_crafting_type
from tools.roller.validators import ValidatorFactory


class RollerConfig:
    def __init__(self, config_file_path):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        f = open(config_file_path)
        self.data = json.load(f)
        f.close()
        self.config_items = []
        self._validate_config()

    def get_num_items(self):
        return len(self.data['items'])

    def get_items(self):
        return self.data['items']

    def _validate_config(self):
        raw_items = self.data['items']
        item_positions = {}
        for raw_item in raw_items:
            position = raw_item['inventory_position']
            assert type(position) is list
            assert len(position) == 2
            assert (0 <= position[0] <= 4)
            assert (0 <= position[1] <= 11)
            assert tuple(position) not in item_positions.keys()

            # Get validator for individual crafting type.
            validator = ValidatorFactory.get_validator(
                get_crafting_type(raw_item['crafting_type']))
            validator.validate(raw_item)

            # Validated.
            # Mark the position as True and get internal representation of item
            # from the raw_item obtained from config.
            item_positions[tuple(position)] = True
            raw_item['item_options'] = validator.create_item_options(raw_item)
        self.logger.debug("Final parsed config data: {}".format(
            pformat(self.data)))

