from typing import List

from siosa.data.affix import Affix
from siosa.data.poe_item import ItemRarity


class ItemOption:
    """
    Representation of an item option provided via roller config.
    """
    def __init__(self, item_class, rarity, name, affixes: List[Affix]):
        """
        Args:
            item_class:
            rarity:
            name:
            affixes:
        """
        self.item_class = item_class
        self.rarity = ItemRarity(rarity)
        self.name = name
        self.affixes = affixes

    def _str(self):
        return "Name: {}, Rarity: {}, Class: {}, Affixes({}): {}".format(
            self.name,
            self.rarity,
            self.item_class,
            len(self.affixes),
            ", ".join([str(affix) for affix in self.affixes]))

    def __repr__(self):
        return self._str()

    def __str__(self):
        return self._str()

    def get_prefixes(self) -> List[Affix]:
        return [x for x in self.affixes if x.is_prefix()]

    def get_suffixes(self)-> List[Affix]:
        return [x for x in self.affixes if not x.is_prefix()]

    def get_num_affixes(self):
        return len(self.affixes)

    def get_num_prefixes(self):
        return len([x for x in self.affixes if x.is_prefix()])

    def get_num_suffixes(self):
        return self.get_num_affixes() - self.get_num_prefixes()
