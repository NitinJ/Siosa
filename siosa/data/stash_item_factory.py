import logging

from siosa.data.poe_currencies import *
from siosa.data.poe_item import ItemType
from siosa.network.poe_api import PoeApi
from siosa.resources.resource import Resource

# Keys that are only present in the item (data obtained from stash) if item
# is a currency item.
STASH_CURRENCY_KEYS = ["stackSize", "maxStackSize"]
STASH_ITEM_KEYS = []

FRAMETYPE_TO_RARITY = {
    0: 'Normal',
    1: 'Magic',
    2: 'Rare',
    3: 'Unique',
    4: 'Gem',
    5: 'Currency',
    6: 'Divination Card'
}


class StashItemFactory:
    """Creates poe items from poe stash api.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.poe_api = PoeApi()

    def get_item(self, item_data):
        """Creates a POE item from data obtained from stash.

        Args:
            stash_data (dict): Dictionary containing data for the item obtained
            from stash API
        """
        if not item_data:
            return None
        self.logger.debug("Getting item from stash api data")
        type = self._get_stash_item_type(item_data)

        self.logger.debug("Got {} from stash data".format(type))
        if type == ItemType.CURRENCY:
            return self._create_currency_item(item_data)
        elif type == ItemType.ITEM:
            return self._create_general_item(item_data)
        return None

    def _create_currency_item(self, item_data):
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
        if not set.isdisjoint(set(STASH_CURRENCY_KEYS), set(data.keys())):
            return ItemType.CURRENCY
        else:
            return ItemType.ITEM

    def _get(self, obj, key, fallback):
        return obj[key] if key in obj.keys() else fallback

    def _get_rarity_of_stash_item(self, item_data):
        frametype = self._get(item_data, 'frameType', 0)
        return self._get(FRAMETYPE_TO_RARITY, frametype, 'Normal')

    def _create_general_item(self, item_data):
        self.logger.debug("Creating general item from stash data")
        info = {
            'rarity': self._get_rarity_of_stash_item(item_data),
            'name': self._get(item_data, 'name', ''),
            'type_line': self._get(item_data, 'typeLine', ''),
            'ilvl': self._get(item_data, 'ilvl', ''),
            'corrupted': self._get(item_data, 'corrupted', ''),
            'unidentified': self._get(item_data, 'identified', ''),
            'note': self._get(item_data, 'note', ''),
            'influences': self._get(item_data, 'influences', {}),
        }
        item = Item(item_info=info, item_type=ItemType.ITEM)
        self.logger.debug("Created general item [{}]".format(str(item)))
        return item
