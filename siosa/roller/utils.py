from typing import List

from siosa.data.affix import Affix
from siosa.data.poe_currencies import CurrencyType
from siosa.data.poe_item import Item
from siosa.location.location_factory import Locations, LocationFactory


CURRENCY_LOCATIONS = {
    CurrencyType.AUGMENTATION.value: Locations.CURRENCY_AUGMENTATION,
    CurrencyType.ALTERATION.value: Locations.CURRENCY_ALTERATION,
    CurrencyType.TRANSMUTATION.value: Locations.CURRENCY_TRANSMUTATION,
    CurrencyType.REGAL.value: Locations.CURRENCY_REGAL,
    CurrencyType.SCOURING.value: Locations.CURRENCY_SCOURING,
    CurrencyType.CHANCE.value: Locations.CURRENCY_CHANCE,
    CurrencyType.CHAOS.value: Locations.CURRENCY_CHAOS,
    CurrencyType.ALCHEMY.value: Locations.CURRENCY_ALCHEMY
}


def item_contains_all_affixes(in_game_item: Item, affixes: List[Affix]):
    """
    Args:
        in_game_item:
        affixes:
    """
    return all([item_contains_affix(
        in_game_item, affix) for affix in affixes])


def item_contains_affix(in_game_item: Item, affix: Affix):
    """
    Args:
        in_game_item:
        affix:
    """
    if affix.is_prefix():
        return affix_match_any(in_game_item.get_prefixes(), affix)
    return affix_match_any(in_game_item.get_suffixes(), affix)


def affix_match_any(affixes: List[Affix], required_affix: Affix):
    """
    Args:
        affixes:
        required_affix:
    """
    return any([affix_match(affix, required_affix) for affix in affixes])


def affix_match_all(affixes: List[Affix], required_affix: Affix):
    """
    Args:
        affixes:
        required_affix:
    """
    return all([affix_match(affix, required_affix) for affix in affixes])


def affix_match(affix: Affix, required_affix: Affix):
    """
    Args:
        affix:
        required_affix:
    """
    if affix.type != required_affix.type:
        return False

    if required_affix.name and affix.name.lower() != required_affix.name:
        return False
    if required_affix.tier and affix.tier > required_affix.tier:
        return False
    if required_affix.str_val:
        return affix.str_val.lower().find(required_affix.str_val) > -1
    return True


def get_inventory00():
    return LocationFactory().get(Locations.INVENTORY_0_0)


def get_currency_location(currency_type: CurrencyType):
    """
    Args:
        currency_type:
    """
    if currency_type.value not in CURRENCY_LOCATIONS.keys():
        return None
    return LocationFactory().get(CURRENCY_LOCATIONS[currency_type.value])


def get_item_location():
    return LocationFactory().get(Locations.ITEM_LOCATION)
