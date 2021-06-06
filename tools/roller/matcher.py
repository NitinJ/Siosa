import logging

from tools.roller.utils import *


class MatcherFactory:
    def __init__(self):
        pass

    @staticmethod
    def get_matcher(item, crafting_type):
        # TODO: Add more matcher types if required and generate them here.
        return Matcher(item)


class Matcher:
    def __init__(self, item):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.base_name = item['base_name']
        self.item = item
        self.item_options = item['item_options']

    def matches(self, in_game_item):
        if not self.base_match(in_game_item):
            raise WrongBaseItemException("Wrong base item!")

        # If any item option matches, it's a match.
        for item_option in self.item_options:
            if not in_game_item.rarity == item_option.rarity:
                continue
            if item_contains_all_affixes(in_game_item, item_option.affixes):
                self.logger.debug(
                    "All affixes matched for item_option: {}".format(
                        item_option.affixes))
                return True, item_option
        return False, None

    def base_match(self, in_game_item):
        return in_game_item.name.find(self.base_name) > -1


class WrongBaseItemException(Exception):
    pass
