from tools.roller.crafting_type import CraftingType
from tools.roller.currency import Currency
from tools.roller.matcher import WrongBaseItemException, Matcher
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
        elif crafting_type == CraftingType.CHANCING:
            return ChancingCrafter(item)
        elif crafting_type == CraftingType.CHAOS:
            return ChaosCrafter(item)
        return None


class Crafter:
    def __init__(self, item):
        self.matcher = Matcher(item)
        self.item = item
        self.item_options = item['item_options']

    def get_crafting_type(self):
        raise NotImplementedError

    def done(self, in_game_item):
        """
        Returns whether the crafter is done crafting.
        Args:
            in_game_item: The in game item.
        Returns: A tuple of whether crafter succeeded in crafting & the next
        currency to use in case it didn't. If next currency to use is None,
        means item cannot be further crafted.
        """
        try:
            matched, matched_item_option = self.matcher.matches(in_game_item)
        except WrongBaseItemException as err:
            # Wrong item base. Return with failure.
            return False, None
        next_currency_to_use = self._get_next_currency_to_use(
            in_game_item, matched, matched_item_option)
        return matched, next_currency_to_use

    def _get_next_currency_to_use(self, in_game_item, matched, matched_item_option):
        """
        Returns the next currency to use on the item given the item_option it
        matched.
        Args:
            in_game_item: The in game item.
            matched: Whether the in game item matched an item option
            matched_item_option: The item option that the in game item matched.
                None if it didn't match any item_option
        Returns:
            Currency to use or None if no currency is to be used and crafting
            is complete.
        """
        raise NotImplementedError


class AlterationCrafter(Crafter):
    def __init__(self, item):
        Crafter.__init__(self, item)

    def _get_next_currency_to_use(self, in_game_item, matched, matched_item_option):
        if matched:
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

    def _get_next_currency_to_use(self, in_game_item, matched, matched_item_option):
        if matched:
            if matched_item_option.rarity == 'magic':
                return Currency.AUGMENTATION if \
                    in_game_item.get_num_affixes() == 1 else Currency.REGAL
            return None

        if in_game_item.rarity == 'normal':
            return Currency.TRANSMUTATION
        if in_game_item.rarity == 'magic':
            if self._should_use_augment(in_game_item):
                return Currency.AUGMENTATION
            return Currency.ALTERATION
        if in_game_item.rarity == 'rare':
            return Currency.SCOURING
        return None


class ChancingCrafter(Crafter):
    def __init__(self, item):
        Crafter.__init__(self, item)

    def get_crafting_type(self):
        return CraftingType.CHANCING

    def _get_next_currency_to_use(self, in_game_item, matched, matched_item_option):
        if matched or in_game_item == 'unique':
            return None
        if in_game_item.rarity == 'normal':
            return Currency.CHANCE
        return Currency.SCOURING


class ChaosCrafter(Crafter):
    def __init__(self, item):
        Crafter.__init__(self, item)

    def get_crafting_type(self):
        return CraftingType.CHAOS

    def _get_next_currency_to_use(self, in_game_item, matched, matched_item_option):
        if matched or in_game_item.rarity == 'unique':
            return None
        if in_game_item.rarity == 'normal':
            return Currency.ALCHEMY
        if in_game_item.rarity == 'magic':
            return Currency.REGAL
        return Currency.CHAOS
