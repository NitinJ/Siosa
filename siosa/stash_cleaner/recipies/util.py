# Whitelist of item classes that shouldn't be vendored.
import logging

from siosa.data.poe_item import Item

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

ITEM_CLASS_WHITELIST = [
    "Map",
    "FishingRod",
    "MetamorphosisDNA",
    "ExpeditionLogbook",
    "MapFragment",
    "LabyrinthMapItem",
    "AtlasRegionUpgradeItem",
    "DivinationCard",
    "MiscMapItem",
    "StackableCurrency",
    "HeistBlueprint",
    "QuestItem",
    "HeistContract",
    "Incubator",
    "DelveStackableSocketableCurrency",
    "DelveSocketableCurrency",
    "ActiveSkillGem",
    "UniqueFragment",
    "Leaguestone",
    "Currency",
    "IncubatorStackable"
]


def should_vendor_item(item: Item):
    """
    Returns if the given item should be vendored.
    """
    return item.item_class not in ITEM_CLASS_WHITELIST


def remove_recipe_items(recipes, items):
    for recipe in recipes:
        for item in recipe:
            try:
                items.remove(item)
            except:
                logger.warning(
                    "Couldn't remove recipe item from items: {}".format(item))