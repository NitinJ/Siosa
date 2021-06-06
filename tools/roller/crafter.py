from tools.roller.crafting_type import CraftingType
from tools.roller.currency import Currency
from tools.roller.matcher import MatcherFactory
from tools.roller.utils import affix_match_all


class CrafterFactory:
    def __init__(self):
        pass

    @staticmethod
    def get_crafter(item, crafting_type):
        if crafting_type == CraftingType.ALTERATION:
            return AlterationCrafter(item)
        elif crafting_type == CraftingType.ALTERATION_REGAL:
            return AlterationRegalCrafter(item)
        return None


class Crafter:
    def __init__(self, item):
        self.matcher = MatcherFactory.get_matcher(item, self.get_crafting_type())
        self.item = item
        self.item_options = item['item_options']

    def get_crafting_type(self):
        raise NotImplementedError

    def done(self, in_game_item):
        matches, item_option = self.matcher.matches(in_game_item)
        next_currency_to_use = self._get_next_currency_to_use(
            in_game_item, item_option)
        if matches and not next_currency_to_use:
            return True, None
        return False, next_currency_to_use

    def _get_next_currency_to_use(self, in_game_item, item_option):
        """
        Returns the next currency to use on the item given the item_option it
        matched.
        Args:
            in_game_item: The in game item.
            item_option: The item option that the in game item matched. None if
                it didn't match any item_option
        Returns:
            Currency to use or None if no currency is to be used and crafting
            is complete.
        """
        raise NotImplementedError


class AlterationCrafter(Crafter):
    def __init__(self, item):
        Crafter.__init__(self, item)

    def _get_next_currency_to_use(self, in_game_item, item_option):
        if item_option:
            # Crafting complete.
            return None
        if in_game_item.rarity == 'normal':
            return Currency.TRANSMUTATION
        if in_game_item.rarity == 'rare':
            return Currency.SCOURING
        if self._should_use_augment(in_game_item):
            return Currency.AUGMENTATION
        return Currency.ALTERATION

    def get_crafting_type(self):
        return CraftingType.ALTERATION

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
                if item_option.rarity != 'magic':
                    continue
                if item_option.get_num_suffixes() == 0:
                    # Suffix isn't required.
                    continue
                if item_option.get_num_prefixes() == 0 or \
                        affix_match_all(prefix, item_option.get_prefixes()):
                    # Prefix isn't required or prefix matches.
                    return True
        if len(suffixes) > 0:
            suffix = suffixes[0]
            for item_option in self.item_options:
                if item_option.rarity != 'magic':
                    continue
                if item_option.get_num_prefixes() == 0:
                    # Prefix isn't required.
                    continue
                if item_option.get_num_suffixes() == 0 or \
                        affix_match_all(suffix, item_option.get_num_suffixes()):
                    # Suffix isn't required or suffix matches.
                    return True
        return False


class AlterationRegalCrafter(AlterationCrafter):
    def __init__(self, item):
        AlterationCrafter.__init__(self, item)

    def get_crafting_type(self):
        return CraftingType.ALTERATION_REGAL

    def _get_next_currency_to_use(self, in_game_item, item_option):
        if in_game_item.rarity == 'normal':
            return Currency.TRANSMUTATION
        if in_game_item.rarity == 'magic':
            if in_game_item.get_num_affixes() == 1:
                return Currency.AUGMENTATION
            if item_option:
                return Currency.REGAL
            return Currency.ALTERATION
        if in_game_item.rarity == 'rare':
            if item_option:
                # Crafting complete.
                return None
            return Currency.SCOURING
