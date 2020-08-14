import math
from enum import Enum


class ItemType(Enum):
    UNKNOWN = 0
    CURRENCY = 1
    ITEM = 2

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
            return None
        return None

    def __str__(self):
        return "Item type: {}, item_info: {}".format(self.type, str(self.item_info))

class CurrencyStack(Item):
    def __init__(self, currency, quantity, item_info={}):
        self.currency = currency
        self.quantity = quantity
        info = {
            'rarity': 'Currency',
            'type_line': currency.name,
            'stack_size': quantity,
            'max_stack_size': currency.max_stack_in_trade
        }
        item_info.update(info)
        Item.__init__(self, item_info=item_info, item_type=ItemType.CURRENCY)
    
    def is_partial(self):
        return (not self.quantity.is_integer())
    
    def get_total_value_in_chaos(self):
        return math.floor(self.currency.get_value_in_chaos() * self.quantity)
