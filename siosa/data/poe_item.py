import math
from enum import Enum


class ItemType(Enum):
    UNKNOWN = 0
    CURRENCY = 1
    ITEM = 2
    GEM = 3
    DIVINATION_CARD = 4
    FRAGMENT = 5
    DELIRIUM_ORB = 6
    CATALYST = 7
    OIL = 8
    INCUBATOR = 9
    SCARAB = 10
    DELVE_RESONATOR = 11
    DELVE_FOSSIL = 12
    MAP = 13

class Item(object):
    def __init__(self, item_info={}, item_type=ItemType.UNKNOWN):
        # Internal type.
        self.type = item_type

        # Item info.
        self.item_info = {
            'rarity': '',
            'type_line': '',
            'name': '',
            'identified': '',
            'corrupted': '',
            'ilvl': '',
            'implicit_mods': '',
            'explicit_mods': '',
            'influences': '',
            'stack_size': '',
            'max_stack_size': '',
            'note': ''
        }
        self.item_info.update(item_info)

    def get_price(self):
        if not self.item_info['note']:
            # TODO(): Parse item note and get price in currency.
            return None
        return None

    def __str__(self):
        return "Item type: {}, item_info: {}".format(self.type, str(self.item_info))

    def __eq__(self, other):
        return self.type == other.type and str(self.item_info) == str(other.item_info)