from siosa.data.poe_currencies import CurrencyType
from siosa.data.poe_item import Item, ItemRarity
from siosa.roller.crafting_type import CraftingType
from siosa.roller.item_option import ItemOption
from siosa.roller.matcher import Matcher, WrongBaseItemException
from siosa.roller.utils import affix_match_all


class CrafterFactory:
    def __init__(self):
        pass

    @staticmethod
    def get_crafter(item, crafting_type: CraftingType):
        """
        Args:
            item:
            crafting_type:
        """
        if crafting_type == CraftingType.ALTERATION:
            return AlterationCrafter(item)
        elif crafting_type == CraftingType.ALTERATION_REGAL:
            return AlterationRegalCrafter(item)
        elif crafting_type == CraftingType.CHANCING:
            return ChancingCrafter(item)
        elif crafting_type == CraftingType.CHAOS:
            return ChaosCrafter(item)
        elif crafting_type == CraftingType.ALCHEMY:
            return AlchemyCrafter(item)
        return None


class Crafter:
    def __init__(self, item):
        """
        Args:
            item:
        """
        self.matcher = Matcher(item)
        self.item = item
        self.item_options = item['item_options']

    def get_crafting_type(self):
        raise NotImplementedError

    def done(self, in_game_item: Item):
        """Returns whether the crafter is done crafting. :param in_game_item:
        The in game item.

        Returns: A tuple of whether crafter succeeded in crafting & the next
        currency to use in case it didn't. If next currency to use is None,
        means item cannot be further crafted.

        Args:
            in_game_item:
        """
        try:
            matched, matched_item_option = self.matcher.matches(in_game_item)
        except WrongBaseItemException as err:
            # Wrong item base. Return with failure.
            return False, None
        next_currency_to_use = self._get_next_currency_to_use(
            in_game_item, matched, matched_item_option)
        done = matched and next_currency_to_use is None
        return done, next_currency_to_use

    def _get_next_currency_to_use(self, in_game_item: Item, matched, matched_item_option):
        """Returns the next currency to use on the item given the item_option it
        matched. :param in_game_item: The in game item. :param matched: Whether
        the in game item matched an item option :param matched_item_option: The
        item option that the in game item matched.

            None if it didn't match any item_option

        Args:
            in_game_item:
            matched:
            matched_item_option:

        Returns:
            Currency to use or None if no currency is to be used and crafting is
            complete.
        """
        raise NotImplementedError


class AlterationCrafter(Crafter):
    def __init__(self, item):
        """
        Args:
            item:
        """
        Crafter.__init__(self, item)

    def _get_next_currency_to_use(self, in_game_item: Item, matched, matched_item_option):
        """
        Args:
            in_game_item:
            matched:
            matched_item_option:
        """
        if matched:
            # Crafting complete.
            return None
        if in_game_item.get_rarity() == ItemRarity.NORMAL:
            return CurrencyType.TRANSMUTATION
        if in_game_item.get_rarity() == ItemRarity.RARE:
            return CurrencyType.SCOURING
        if self._should_use_augment(in_game_item):
            return CurrencyType.AUGMENTATION
        return CurrencyType.ALTERATION

    def get_crafting_type(self):
        return CraftingType.ALTERATION

    def _should_use_augment(self, in_game_item: Item):
        """
        Args:
            in_game_item:
        """
        if in_game_item.get_num_affixes() > 1 or \
                in_game_item.get_rarity() != ItemRarity.MAGIC:
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
                if item_option.rarity != ItemRarity.MAGIC:
                    continue
                if item_option.get_num_suffixes() == 0:
                    # Suffix isn't required.
                    continue
                if item_option.get_num_prefixes() == 0 or \
                        affix_match_all(item_option.get_prefixes(), prefix):
                    # Prefix isn't required or prefix matches.
                    return True
        if len(suffixes) > 0:
            suffix = suffixes[0]
            for item_option in self.item_options:
                if item_option.rarity != ItemRarity.MAGIC:
                    continue
                if item_option.get_num_prefixes() == 0:
                    # Prefix isn't required.
                    continue
                if item_option.get_num_suffixes() == 0 or \
                        affix_match_all(item_option.get_num_suffixes(), suffix):
                    # Suffix isn't required or suffix matches.
                    return True
        return False


class AlterationRegalCrafter(AlterationCrafter):
    def __init__(self, item):
        """
        Args:
            item:
        """
        AlterationCrafter.__init__(self, item)

    def get_crafting_type(self):
        return CraftingType.ALTERATION_REGAL

    def _get_next_currency_to_use(self, in_game_item: Item, matched, matched_item_option: ItemOption):
        """
        Args:
            in_game_item:
            matched:
            matched_item_option:
        """
        if matched:
            if matched_item_option.rarity == ItemRarity.MAGIC:
                return CurrencyType.AUGMENTATION if \
                    in_game_item.get_num_affixes() == 1 else CurrencyType.REGAL
            return None

        if in_game_item.get_rarity() == ItemRarity.NORMAL:
            return CurrencyType.TRANSMUTATION
        if in_game_item.get_rarity() == ItemRarity.MAGIC:
            if self._should_use_augment(in_game_item):
                return CurrencyType.AUGMENTATION
            return CurrencyType.ALTERATION
        if in_game_item.get_rarity() == ItemRarity.RARE:
            return CurrencyType.SCOURING
        return None


class ChancingCrafter(Crafter):
    def __init__(self, item):
        """
        Args:
            item:
        """
        Crafter.__init__(self, item)

    def get_crafting_type(self):
        return CraftingType.CHANCING

    def _get_next_currency_to_use(self, in_game_item, matched, matched_item_option: ItemOption):
        """
        Args:
            in_game_item:
            matched:
            matched_item_option:
        """
        if matched or in_game_item.get_rarity() == 'unique':
            return None
        if in_game_item.get_rarity() == ItemRarity.NORMAL:
            return CurrencyType.CHANCE
        return CurrencyType.SCOURING


class ChaosCrafter(Crafter):
    def __init__(self, item):
        """
        Args:
            item:
        """
        Crafter.__init__(self, item)

    def get_crafting_type(self):
        return CraftingType.CHAOS

    def _get_next_currency_to_use(self, in_game_item: Item, matched, matched_item_option: ItemOption):
        """
        Args:
            in_game_item:
            matched:
            matched_item_option:
        """
        if matched or in_game_item.get_rarity() == 'unique':
            return None
        if in_game_item.get_rarity() == ItemRarity.NORMAL:
            return CurrencyType.ALCHEMY
        if in_game_item.get_rarity() == ItemRarity.MAGIC:
            return CurrencyType.REGAL
        return CurrencyType.CHAOS


class AlchemyCrafter(Crafter):
    def __init__(self, item):
        """
        Args:
            item:
        """
        Crafter.__init__(self, item)

    def get_crafting_type(self):
        return CraftingType.ALCHEMY_SCOUR

    def _get_next_currency_to_use(self, in_game_item: Item, matched, matched_item_option: ItemOption):
        """
        Args:
            in_game_item:
            matched:
            matched_item_option:
        """
        if matched:
            return None
        if in_game_item.get_rarity() == ItemRarity.NORMAL:
            return CurrencyType.ALCHEMY
        if in_game_item.get_rarity() == ItemRarity.RARE:
            return CurrencyType.SCOURING
        return CurrencyType.ALCHEMY
