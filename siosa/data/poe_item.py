from enum import Enum

from siosa.data.ggpk.base_items import BaseItems


class ItemInfluences(Enum):
    SHAPER = 'shaper'
    ELDER = 'elder'
    CRUSADER = 'crusader'
    WARLORD = 'warlord'
    HUNTER = 'hunter'
    REDEEMER = 'redeemer'


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
    def __init__(self, item_info=None, affixes=None,
                 item_type=ItemType.UNKNOWN):
        # Internal type.
        """
        Args:
            item_info:
            item_type:
        """
        if affixes is None:
            affixes = []
        if item_info is None:
            item_info = {}
        self.type = item_type
        self.affixes = affixes
        self.item_class = 'Unknown'

        # Item info.
        self.item_info = {
            'rarity': '',
            'type_line': '',
            'base_type': '',
            'name': '',
            'identified': '',
            'corrupted': '',
            'ilvl': 0,
            'implicit_mods': '',
            'explicit_mods': '',
            'influences': {},
            'stack_size': 1,
            'max_stack_size': 1,
            'note': '',
            'w': None,
            'h': None
        }
        self.item_info.update(item_info)
        self._update_dimensions()
        self._update_item_class()

    def is_flask(self):
        return self.item_class in [
            "HybridFlask", "LifeFlask",
            "ManaFlask", "UtilityFlask"]

    def is_gem(self):
        return self.type == ItemType.GEM

    def get_level(self):
        return int(self.item_info['ilvl'])

    def is_identified(self):
        if self.item_info['identified']:
            return True
        return False

    def is_influenced(self):
        return len(self.item_info['influences']) > 0

    def has_influence(self, influence: ItemInfluences):
        return influence in self.item_info['influences']

    def is_two_handed_weapon(self):
        return self.item_class in ["Bow", "Staff",
                                   "Warstaff", "TwoHandMace",
                                   "TwoHandSword", "TwoHandAxe"]

    def is_one_handed_weapon(self):
        return self.item_class in ["RuneDagger", "Sceptre",
                                   "Wand", "Dagger",
                                   "OneHandAxe",
                                   "OneHandSword",
                                   "OneHandMace",
                                   "OneHandSwordThrusting",
                                   "Claw"]

    def is_shield(self):
        return self.item_class == "Shield"

    def is_helmet(self):
        return self.item_class == "Helmet"

    def is_body_armour(self):
        return self.item_class == "BodyArmour"

    def is_gloves(self):
        return self.item_class == "Gloves"

    def is_boots(self):
        return self.item_class == "Boots"

    def is_belt(self):
        return self.item_class == "Belt"

    def is_amulet(self):
        return self.item_class == "Amulet"

    def is_ring(self):
        return self.item_class == "Ring"

    def is_quiver(self):
        return self.item_class == "Quiver"

    def get_max_stack_size(self):
        return self.item_info['max_stack_size']

    def get_stack_size(self):
        return self.item_info['stack_size']

    def is_stackable(self):
        return self.item_info['max_stack_size'] > 1

    def _update_item_class(self):
        key = self.item_info['base_type'] if \
            self.item_info['base_type'] else self.item_info['type_line']
        data = BaseItems.get(key)
        if not data:
            return
        self.item_class = data['item_class']

    def _update_dimensions(self):
        key = self.item_info['base_type'] if \
            self.item_info['base_type'] else self.item_info['type_line']
        data = BaseItems.get(key)
        if not data:
            return
        self.set_dimensions(data['inventory_width'], data['inventory_height'])

    def set_dimensions(self, w, h):
        """
        Args:
            w:
            h:
        """
        if w <= 0 or h <= 0:
            return
        self.item_info.update({
            'w': w,
            'h': h
        })

    def get_prefixes(self):
        return [x for x in self.affixes if x.is_prefix()]

    def get_suffixes(self):
        return [x for x in self.affixes if x.is_suffix()]

    def get_num_affixes(self):
        return len(self.affixes)

    def get_num_prefixes(self):
        return self.item_info['n_prefixes']

    def get_num_suffixes(self):
        return self.item_info['n_suffixes']

    def get_dimensions(self):
        return self.item_info['w'], self.item_info['h']

    def get_price(self):
        if not self.item_info['note']:
            # TODO(): Parse item note and get price in currency.
            return None
        return None

    def get_rarity(self):
        return self.item_info['rarity']

    def get_name(self):
        return self.item_info['type_line']

    def get_base_type(self):
        return self.item_info['base_type']

    def get_trade_name(self):
        if self.item_info['name'] and self.item_info['type_line']:
            return "{} {}".format(self.item_info['name'],
                                  self.item_info['type_line'])
        elif self.item_info['type_line']:
            return self.item_info['type_line']
        else:
            return self.item_info['name']

    def is_same_kind(self, other):
        def get_item_info_for_comparison(item):
            item_info = item.item_info.copy()
            del item_info['ilvl']
            del item_info['note']
            del item_info['stack_size']
            del item_info['implicit_mods']
            del item_info['explicit_mods']
            return item_info

        return self.type == other.type and \
               str(get_item_info_for_comparison(self)) == \
               str(get_item_info_for_comparison(other))

    def __str__(self):
        return "Item type: {}, item_info: {}".format(self.type,
                                                     str(self.item_info))

    def __eq__(self, other):
        return self.type == other.type and str(self.item_info) == str(
            other.item_info)
