import logging

from tools.roller.crafting_type import CraftingType
from tools.roller.currency import Currency


class MatcherFactory:
    def __init__(self):
        pass

    @staticmethod
    def get_matcher(item, crafting_type):
        if crafting_type == CraftingType.ALTERATION:
            return AlterationMatcher(item, crafting_type)
        return None


class Matcher:
    def __init__(self, item, crafting_type):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.crafting_type = crafting_type
        self.item = item
        self.base_name = item['base_name']
        self.item_options = item['item_options']

    def matches(self, in_game_item):
        if not self.base_match(in_game_item):
            return False

        # If any item option matches, it's a match.
        for item_option in self.item_options:
            all_affixes_in_item_option = []
            all_affixes_in_item_option.extend(item_option['prefixes'])
            all_affixes_in_item_option.extend(item_option['suffixes'])
            if self._item_contains_all_affixes(
                    in_game_item, all_affixes_in_item_option):
                self.logger.debug("All affixes matched for item_option: {}".format(all_affixes_in_item_option))
                return True, None

        if in_game_item.rarity == 'normal':
            return False, Currency.TRANSMUTATION

        return False, self._get_next_currency_to_use(in_game_item)

    def _get_next_currency_to_use(self, in_game_item):
        raise NotImplementedError

    def base_match(self, in_game_item):
        return in_game_item.name.find(self.base_name) > -1

    def _item_contains_all_affixes(self, in_game_item, affixes):
        return all([self._item_contains_affix(
            in_game_item, affix) for affix in affixes])

    def _item_contains_affix(self, in_game_item, affix):
        if affix.type == 'prefix':
            return self._affix_match_any(in_game_item.get_prefixes(), affix)
        return self._affix_match_any(in_game_item.get_suffixes(), affix)

    def _affix_match_any(self, affixes, required_affix):
        return any([self._affix_match(affix, required_affix) for affix in affixes])

    def _affix_match_all(self, affixes, required_affix):
        return any([self._affix_match(affix, required_affix) for affix in affixes])

    def _affix_match(self, affix, required_affix):
        if affix.type != required_affix.type:
            return False
        if affix.name != required_affix.name:
            return False
        if required_affix.tier and affix.tier > required_affix.tier:
            return False
        if required_affix.str_val:
            return affix.str_val.find(required_affix.str_val) > -1
        return True


class AlterationMatcher(Matcher):
    def _get_next_currency_to_use(self, in_game_item):
        if self._should_use_augment(in_game_item):
            return Currency.AUGMENTATION
        return Currency.ALTERATION

    def _should_use_augment(self, in_game_item):
        if in_game_item.get_num_affixes() > 1 or \
                in_game_item.rarity != 'magic':
            return False
        prefixes = in_game_item.get_prefixes()
        suffixes = in_game_item.get_suffixes()
        assert len(prefixes) < 2 and len(suffixes) < 2
        if len(prefixes) > 0:
            prefix = prefixes[0]
            # All the item options which have a suffix and either their prefix
            # matches the current prefix or don't have a prefix are valid
            # options.
            for item_option in self.item_options:
                if len(item_option['suffixes']) == 0:
                    # Suffix isn't required.
                    continue
                if len(item_option['prefixes']) == 0 or \
                        self._affix_match_all(prefix, item_option['prefixes']):
                    # Prefix isn't required or prefix matches.
                    return True
        if len(suffixes) > 0:
            suffix = suffixes[0]
            for item_option in self.item_options:
                if len(item_option['prefixes']) == 0:
                    # Prefix isn't required.
                    continue
                if len(item_option['suffixes']) == 0 or \
                        self._affix_match_all(suffix, item_option['suffixes']):
                    # Suffix isn't required or suffix matches.
                    return True
        return False








