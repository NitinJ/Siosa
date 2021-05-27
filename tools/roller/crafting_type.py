from enum import Enum


class CraftingType(Enum):
    ALTERATION = 'alteration'
    ALTERATION_REGAL = 'alteration_regal'
    CHAOS = 'chaos'
    CHANCE = 'chance'


def get_crafting_type(type_str):
    try:
        return CraftingType(type_str)
    except:
        return None
