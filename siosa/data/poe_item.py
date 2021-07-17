from enum import Enum

from siosa.resources.ggpk_data.base_items import BaseItems


class ItemRarity(Enum):
    UNKNOWN = 'Unknown'
    CURRENCY = 'Currency'
    GEM = 'Gem'
    DIVINATION_CARD = 'Divination Card'
    NORMAL = 'Normal'
    MAGIC = 'Magic'
    RARE = 'Rare'
    UNIQUE = 'Unique'


class ItemType(Enum):
    """Types of items. Next value: 23

    Args:
        Enum (int): Unique int value for item
    """
    UNKNOWN = 0
    CURRENCY = 1

    # rarity: Normal,Magic,Rare,Unique
    ITEM = 2

    GEM = 3  # rarity: Gem
    DIVINATION_CARD = 4  # rarity: divination card

    # rarity: Currency
    DELIRIUM_ORB = 6
    CATALYST = 7
    OIL = 8
    DELVE_RESONATOR = 11
    DELVE_FOSSIL = 12
    SPLINTER = 14
    SIMULACRUM_SPLINTER = 20
    ESSENCE = 21

    # rarity: Normal
    INCUBATOR = 9
    SCARAB = 10
    FRAGMENT = 5
    MAP = 13
    OFFERING = 15
    DIVINE_VESSEL = 16
    TIMELESS_EMBLEM = 17
    ORGAN = 18
    SIMULACRUM = 19
    BREACHSTONE = 22


class Item(object):
    def __init__(self, item_info={}, item_type=ItemType.UNKNOWN):
        # Internal type.
        """
        Args:
            item_info:
            item_type:
        """
        self.type = item_type

        # Item info.
        self.item_info = {
            'rarity': '',
            'type_line': '',
            'base_type': '',
            'name': '',
            'identified': '',
            'corrupted': '',
            'ilvl': '',
            'implicit_mods': '',
            'explicit_mods': '',
            'influences': '',
            'stack_size': '',
            'max_stack_size': '',
            'note': '',
            'w': None,
            'h': None
        }
        self.item_info.update(item_info)
        self._update_dimensions()

    def _update_dimensions(self):
        dim = BaseItems.get_item_dimensions(self.item_info['base_type'])
        if dim:
            self.set_dimensions(dim[0], dim[1])

    def set_dimensions(self, w, h):
        """
        Args:
            w:
            h:
        """
        if w <= 0 or h <=0:
            return
        self.item_info.update({
            'w': w,
            'h': h
        })

    def get_dimensions(self):
        return self.item_info['w'], self.item_info['h']

    def get_price(self):
        if not self.item_info['note']:
            # TODO(): Parse item note and get price in currency.
            return None
        return None

    def get_name(self):
        return self.item_info['type_line']

    def get_full_name(self):
        if self.item_info['name'] and self.item_info['type_line']:
            return "{} {}".format(self.item_info['name'], self.item_info['type_line'])
        elif self.item_info['type_line']:
            return self.item_info['type_line']
        else:
            return self.item_info['name']

    def __str__(self):
        return "Item type: {}, item_info: {}".format(self.type, str(self.item_info))

    def __eq__(self, other):
        return self.type == other.type and str(self.item_info) == str(other.item_info)
