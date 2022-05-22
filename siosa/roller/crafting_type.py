from enum import Enum


class CraftingType(Enum):
    ALTERATION = 'alteration'
    ALTERATION_REGAL = 'alteration_regal'
    CHAOS = 'chaos'
    CHANCING = 'chancing'
    ALCHEMY = 'alchemy'


def get_crafting_type(type_str):
    """
    Args:
        type_str:
    """
    return CraftingType(type_str)
