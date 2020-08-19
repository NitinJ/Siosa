import math
from enum import Enum

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
    """Types of items.
    Next value: 22
    
    Args:
        Enum (int): Unique int value for item
    """
    UNKNOWN = 0
    CURRENCY = 1
    ITEM = 2 #rarity: Normal,Magic,Rare,Unique
    GEM = 3 #rarity: Gem
    DIVINATION_CARD = 4 #rarity: divination card
    
    DELIRIUM_ORB = 6 #rarity: Currency
    CATALYST = 7 #rarity: Currency
    OIL = 8 #rarity: Currency
    DELVE_RESONATOR = 11 #rarity: Currency
    DELVE_FOSSIL = 12 #rarity: Currency
    SPLINTER = 14 #rarity: Currency
    SIMULACRUM_SPLINTER = 20 #rarity: Currency
    ESSENCE = 21 #rarity: Currency 
        
    INCUBATOR = 9 #rarity: Normal
    SCARAB = 10 #rarity: Normal
    FRAGMENT = 5 #rarity: Normal
    MAP = 13 #rarity: Normal
    OFFERING = 15 #rarity: Normal
    DIVINE_VESSEL = 16 #rarity: Normal
    TIMELESS_EMBLEM = 17 #rarity: Normal
    ORGAN = 18 #rarity: Normal
    SIMULACRUM = 19 #rarity: Normal
    

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

    def get_name(self):
        return self.item_info['type_line']
        
    def __str__(self):
        return "Item type: {}, item_info: {}".format(self.type, str(self.item_info))

    def __eq__(self, other):
        return self.type == other.type and str(self.item_info) == str(other.item_info)