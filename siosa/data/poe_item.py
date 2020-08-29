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
    Next value: 23
    
    Args:
        Enum (int): Unique int value for item
    """
    UNKNOWN = 0
    CURRENCY = 1
    
    #rarity: Normal,Magic,Rare,Unique
    ITEM = 2 
    
    GEM = 3 #rarity: Gem
    DIVINATION_CARD = 4 #rarity: divination card
    
    #rarity: Currency
    DELIRIUM_ORB = 6
    CATALYST = 7
    OIL = 8
    DELVE_RESONATOR = 11
    DELVE_FOSSIL = 12
    SPLINTER = 14
    SIMULACRUM_SPLINTER = 20
    ESSENCE = 21 
    
     #rarity: Normal
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
    
    def get_full_name(self):
        return "{} {}".format(self.item_info['name'], self.item_info['type_line'])
        
    def __str__(self):
        return "Item type: {}, item_info: {}".format(self.type, str(self.item_info))

    def __eq__(self, other):
        return self.type == other.type and str(self.item_info) == str(other.item_info)