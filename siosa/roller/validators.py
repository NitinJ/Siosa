import itertools
import logging

from siosa.data.affix import Affix
from siosa.data.poe_item import ItemRarity
from siosa.roller.crafting_type import CraftingType, get_crafting_type
from siosa.roller.item_option import ItemOption


class ValidatorFactory:
    def __init__(self):
        pass

    @staticmethod
    def get_validator(crafting_type):
        """
        Args:
            crafting_type:
        """
        if crafting_type == CraftingType.ALTERATION:
            return AlterationCraftingValidator()
        elif crafting_type == CraftingType.ALTERATION_REGAL:
            return AlterationRegalCraftingValidator()
        elif crafting_type == CraftingType.CHANCING:
            return ChancingCraftingValidator()
        elif crafting_type == CraftingType.CHAOS:
            return RareCraftingValidator()
        elif crafting_type == CraftingType.ALCHEMY:
            return RareCraftingValidator()
        return None


class Validator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

    def validate(self, raw_item):
        """Validates whether the config is correct or not. :param raw_item: Item
        obtained from raw config.

        Returns: None

        Args:
            raw_item:
        """
        crafting_type = get_crafting_type(raw_item['crafting_type'])
        assert crafting_type
        raw_item['crafting_type'] = crafting_type

        assert raw_item['item_options']
        assert len(raw_item['item_options']) > 0
        self._validate_internal(raw_item)

    def create_item_options(self, raw_item):
        """Creates item objects from raw_item objects (obtained from config).
        :param raw_item: Raw item obtained from config, containing item-options

        Args:
            raw_item:

        Returns:
            Item objects which are internal representation of items in roller.
        """
        return [Validator._create_item_from_item_option(item_option) for
                item_option in raw_item['item_options']]

    @staticmethod
    def _get_affix(affix, affix_type):
        """
        Args:
            affix:
            affix_type:
        """
        tier = int(affix['tier']) if 'tier' in affix else None
        return Affix(affix['hint'], affix['name'], tier, affix_type)

    @staticmethod
    def _create_item_from_item_option(raw_item_option):
        """
        Args:
            raw_item_option:
        """
        affixes = []
        if 'prefixes' in raw_item_option and raw_item_option['prefixes']:
            for prefix in raw_item_option['prefixes']:
                affixes.append(Validator._get_affix(prefix, 'Prefix'))
        if 'suffixes' in raw_item_option and raw_item_option['suffixes']:
            for suffix in raw_item_option['suffixes']:
                affixes.append(Validator._get_affix(suffix, 'Suffix'))
        return ItemOption('', raw_item_option['rarity'], '', affixes)

    def _validate_internal(self, item):
        """
        Args:
            item:
        """
        raise NotImplementedError


class AlterationCraftingValidator(Validator):
    def __init__(self):
        Validator.__init__(self)

    def _validate_internal(self, item):
        """
        Args:
            item:
        """
        for item_option in item['item_options']:
            self._validate_item_option(item_option)

    def _validate_item_option(self, item_option):
        """
        Args:
            item_option:
        """
        prefixes = item_option.get('prefixes', [])
        suffixes = item_option.get('suffixes', [])
        assert (len(prefixes) or len(suffixes))
        for affix in itertools.chain(prefixes, suffixes):
            if affix['name'] and affix['tier']:
                assert affix['tier'] > 0


class AlterationRegalCraftingValidator(AlterationCraftingValidator):
    def __init__(self):
        super().__init__()

    def _validate_internal(self, item):
        """
        Args:
            item:
        """
        AlterationCraftingValidator._validate_internal(self, item)
        num_rare_item_options = 0
        for item_option in item['item_options']:
            if item_option['rarity'] == 'Rare':
                num_rare_item_options += 1
        assert num_rare_item_options > 0


class ChancingCraftingValidator(Validator):
    def __init__(self):
        Validator.__init__(self)

    def _validate_internal(self, item):
        """
        Args:
            item:
        """
        for item_option in item['item_options']:
            self._validate_item_option(item_option)

    def _validate_item_option(self, item_option):
        """
        Args:
            item_option:
        """
        assert item_option['rarity'] == 'Unique'


class RareCraftingValidator(Validator):
    def __init__(self):
        Validator.__init__(self)

    def _validate_internal(self, item):
        """
        Args:
            item:
        """
        for item_option in item['item_options']:
            self._validate_item_option(item_option)

    def _validate_item_option(self, item_option):
        """
        Args:
            item_option:
        """
        prefixes = item_option['prefixes']
        suffixes = item_option['suffixes']
        assert item_option['rarity'] == 'Rare'
        assert (len(prefixes) or len(suffixes))
        for affix in itertools.chain(prefixes, suffixes):
            if affix['name'] and affix['tier']:
                assert affix['tier'] > 0
