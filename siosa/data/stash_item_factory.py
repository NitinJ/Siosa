import re

from siosa.data.gem import Gem
from siosa.data.map import Map
from siosa.data.poe_currencies import *
from siosa.data.poe_item import ItemType
from siosa.network.poe_api import PoeApi

# Keys that are only present in the item (data obtained from stash) if item
# is a currency item.
STASH_CURRENCY_KEYS = ["stackSize", "maxStackSize"]
STASH_ITEM_KEYS = []

FRAME_TYPE_TO_RARITY = {
    0: ItemRarity.NORMAL,
    1: ItemRarity.MAGIC,
    2: ItemRarity.RARE,
    3: ItemRarity.UNIQUE,
    4: ItemRarity.GEM,
    5: ItemRarity.CURRENCY,
    6: ItemRarity.DIVINATION_CARD
}
GEM_QUALITY_REGEX = "\+(\d*)\%"


class StashItemFactory:
    """Creates poe items from poe stash api."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.poe_api = PoeApi()

    def get_item(self, item_data):
        """Creates a POE item from data obtained from stash.

        Args:
            item_data:
        """
        if not item_data:
            return None
        self.logger.debug("Getting item from stash api data")
        type = self._get_stash_item_type(item_data)

        self.logger.debug("Got {} from stash data".format(type))
        if type == ItemType.CURRENCY:
            return self._create_currency_item(item_data)
        elif type == ItemType.GEM:
            return self._create_gem_item(item_data)
        elif type == ItemType.MAP:
            return self._create_map_item(item_data)
        elif type == ItemType.ITEM:
            return self._create_general_item(item_data)
        return None

    def _create_currency_item(self, item_data):
        """
        Args:
            item_data:
        """
        self.logger.debug("Creating currency item from stash data")
        # name for currency is it's type_line.
        name = self._get(item_data, 'typeLine', '')
        stack_size = self._get(item_data, 'stackSize', 1)
        stack_max_size = self._get(item_data, 'maxStackSize', 10)

        info = {
            'note': self._get(item_data, 'note', '')
        }
        currency = Currency.create(
            name=name,
            max_stack_in_trade=stack_max_size)
        if not currency:
            return None

        item = CurrencyStack(currency, stack_size, item_info=info)
        self.logger.debug("Created currency item [{}]".format(str(item)))
        return item

    def _get_stash_item_type(self, data):
        """
        Args:
            data:
        """
        if not set.isdisjoint(set(STASH_CURRENCY_KEYS), set(data.keys())):
            return ItemType.CURRENCY
        elif data['frameType'] == 4:
            return ItemType.GEM
        elif self._is_map(data):
            return ItemType.MAP
        else:
            # TODO: Add support for more ItemTypes.
            return ItemType.ITEM

    def _is_map(self, item_data):
        return self._get_property(item_data, "Map Tier") is not None

    def _get(self, obj, key, fallback):
        """
        Args:
            obj:
            key:
            fallback:
        """
        return obj[key] if key in obj.keys() else fallback

    def _get_rarity_of_stash_item(self, item_data):
        """
        Args:
            item_data:
        """
        frametype = self._get(item_data, 'frameType', 0)
        return self._get(FRAME_TYPE_TO_RARITY, frametype, 'Normal')

    def _get_item_info(self, item_data):
        return {
            'rarity': self._get_rarity_of_stash_item(item_data),
            'type_line': self._get(item_data, 'typeLine', ''),
            'base_type': self._get(item_data, 'baseType', ''),
            'name': self._get(item_data, 'name', ''),
            'identified': not self._get(item_data, 'identified', ''),
            'corrupted': self._get(item_data, 'corrupted', ''),
            'ilvl': self._get(item_data, 'ilvl', ''),
            'explicit_mods': self._get(item_data, 'explicitMods', []),
            'influences': self._get(item_data, 'influences', {}),
            'stack_size': self._get(item_data, 'stackSize', 1),
            'max_stack_size': self._get(item_data, 'maxStackSize', 1),
            'note': self._get(item_data, 'note', ''),
            'w': self._get(item_data, 'w', 1),
            'h': self._get(item_data, 'h', 1)
        }

    def _get_property(self, item_data, property):
        if 'properties' not in item_data.keys():
            return None
        for prop in item_data['properties']:
            if prop['name'] == property:
                return prop
        return None

    def _get_gem_quality(self, item_data):
        quality_s = self._get_property(item_data, 'Quality')
        if not quality_s:
            return 0
        quality_s = quality_s['values'][0][0]
        match = re.compile(GEM_QUALITY_REGEX).match(quality_s)
        if match:
            return int(match.groups()[0])
        else:
            return 0

    def _create_map_item(self, item_data):
        """
        Args:
            item_data:
        """
        info = self._get_item_info(item_data)
        map_tier = int(self._get_property(item_data, 'Map Tier')['values'][0][0])
        item = Map(map_tier, info)
        self.logger.debug("Created map item [{}]".format(str(item)))
        return item

    def _create_gem_item(self, item_data):
        """
        Args:
            item_data:
        """
        info = self._get_item_info(item_data)
        gem_quality = self._get_gem_quality(item_data)
        gem_level = int(self._get_property(item_data, 'Level')['values'][0][0].split(" ")[0])
        item = Gem(gem_level, gem_quality, info)
        self.logger.debug("Created gem item [{}]".format(str(item)))
        return item

    def _create_general_item(self, item_data):
        """
        Args:
            item_data:
        """
        info = self._get_item_info(item_data)
        item = Item(item_info=info, item_type=ItemType.ITEM)
        self.logger.debug("Created general item [{}]".format(str(item)))
        return item
