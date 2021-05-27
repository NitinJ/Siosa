import json
import logging
from pprint import pprint

from tools.roller.crafting_type import CraftingType, get_crafting_type
from tools.roller.item import Affix


class RollerConfig:
    SUPPORTED_RARITIES = ['magic']

    def __init__(self, config_file_path):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        f = open(config_file_path)
        self.data = json.load(f)
        f.close()
        self._validate_config()

    def get_num_items(self):
        return len(self.data['items'])

    def _validate_config(self):
        items = self.data['items']
        item_positions = {}
        for item in items:
            position = item['inventory_position']
            assert type(position) is list
            assert len(position) == 2
            assert (0 <= position[0] <= 4)
            assert (0 <= position[1] <= 11)
            assert tuple(position) not in item_positions.keys()

            # Get validator for individual crafting type.
            validator = ValidatorFactory.get_validator(
                get_crafting_type(item['crafting_type']))
            validator.validate(item)
            item_positions[tuple(position)] = True
        self.logger.debug("Final parsed config: {}".format(self.data))


class ValidatorFactory:
    def __init__(self):
        pass

    @staticmethod
    def get_validator(crafting_type):
        if crafting_type == CraftingType.ALTERATION:
            return AlterationCraftingValidator()
        # only alteration crafting supported as of now.
        return None


class Validator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

    def validate(self, item):
        crafting_type = get_crafting_type(item['crafting_type'])
        assert crafting_type
        item['crafting_type'] = crafting_type

        assert item['item_options']
        assert len(item['item_options']) > 0
        self._validate_internal(item)

    def _validate_internal(self, item):
        raise NotImplementedError


class AlterationCraftingValidator(Validator):
    def __init__(self):
        Validator.__init__(self)

    def _validate_internal(self, item):
        item_options = item['item_options']
        assert len(item_options) > 0
        parsed_item_options = []

        for item_option in item_options:
            self._validate_item_option(item_option)
            parsed_item_options.append(
                self._convert_item_option(item_option))

        # Replace the vanilla item options with parsed item objects.
        item['item_options'] = parsed_item_options
        self.logger.debug('Parsed item options: {}'.format(
            parsed_item_options))

    def _convert_item_option(self, item_option):
        parsed_item_option = {
            'type': 'magic',
            'prefixes': [],
            'suffixes': []
        }
        if item_option['prefix']:
            tier = item_option['prefix_tier']
            parsed_item_option['prefixes'].append(Affix(
                item_option['prefix_hint'],
                item_option['prefix'],
                int(tier) if tier else None,
                'prefix'))
        if item_option['suffix']:
            tier = item_option['suffix_tier']
            parsed_item_option['suffixes'].append(Affix(
                item_option['suffix_hint'],
                item_option['suffix'],
                int(tier) if tier else None,
                'suffix'))
        return parsed_item_option

    def _validate_item_option(self, item_option):
        assert (item_option['prefix'] or item_option['suffix'])
        if item_option['prefix'] and item_option['prefix_tier']:
            assert item_option['prefix_tier'] > 0
        if item_option['suffix'] and item_option['suffix_tier']:
            assert item_option['suffix_tier'] > 0
