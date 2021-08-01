import logging

from siosa.data.poe_item import Item
from siosa.roller.item_option import ItemOption
from siosa.roller.utils import item_contains_all_affixes


class Matcher:
    def __init__(self, item):
        """
        Args:
            item:
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.item = item
        self.base_name = item['base_name']
        self.item_options = item['item_options']

    def matches(self, in_game_item: Item) -> (bool, ItemOption):
        """
        Args:
            in_game_item:
        """
        if not self.base_match(in_game_item):
            self.logger.debug(
                "Wrong base type: found: {}, expected: {}".format(
                    in_game_item.get_base_type(), self.base_name))
            raise WrongBaseItemException("Wrong base item!")

        # If any item option matches, it's a match.
        for item_option in self.item_options:
            self.logger.debug(
                "Matching in_game_item: {}, item_option: {}".format(
                    in_game_item, item_option))
            if not in_game_item.get_rarity() == item_option.rarity:
                self.logger.debug("Rarity mismatch")
                continue
            if item_contains_all_affixes(in_game_item, item_option.affixes):
                self.logger.debug(
                    "All affixes matched for item_option: {}".format(
                        item_option.affixes))
                return True, item_option
        return False, None

    def base_match(self, in_game_item: Item):
        """
        Args:
            in_game_item:
        """
        return in_game_item.get_base_type().lower().find(self.base_name) > -1


class WrongBaseItemException(Exception):
    pass
