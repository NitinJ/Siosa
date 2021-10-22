import functools
import logging

from siosa.data.poe_item import ItemInfluences, ItemRarity
from siosa.data.stash_item import StashItem
from siosa.stash_cleaner.recipies.recipe import Recipe
from siosa.stash_cleaner.recipies.util import remove_recipe_items

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')


def _split(items, condition):
    is_rare_amulet = lambda \
            item: item.get_rarity() == ItemRarity.RARE and item.is_amulet()
    is_rare_helmet = lambda \
            item: item.get_rarity() == ItemRarity.RARE and item.is_helmet()
    is_rare_gloves = lambda \
            item: item.get_rarity() == ItemRarity.RARE and item.is_gloves()
    is_rare_boots = lambda \
            item: item.get_rarity() == ItemRarity.RARE and item.is_boots()
    is_rare_two_handed = lambda \
            item: item.get_rarity() == ItemRarity.RARE and \
                  item.is_two_handed_weapon()
    is_rare_body_armour = lambda \
            item: item.get_rarity() == ItemRarity.RARE and item.is_body_armour()
    is_rare_belt = lambda \
            item: item.get_rarity() == ItemRarity.RARE and item.is_belt()
    is_rare_ring = lambda \
            item: item.get_rarity() == ItemRarity.RARE and item.is_ring()
    is_rare_one_handed = lambda \
            item: (item.is_one_handed_weapon() or item.is_shield()) and \
                  item.get_rarity() == ItemRarity.RARE
    ret = {
        'amulets': list(
            filter(lambda item: condition(item) and is_rare_amulet(item),
                   items)),
        'helmets': list(
            filter(lambda item: condition(item) and is_rare_helmet(item),
                   items)),
        'gloves': list(
            filter(lambda item: condition(item) and is_rare_gloves(item),
                   items)),
        'boots': list(
            filter(lambda item: condition(item) and is_rare_boots(item),
                   items)),
        'two_handed': list(
            filter(lambda item: condition(item) and is_rare_two_handed(item),
                   items)),
        'body_armour': list(
            filter(lambda item: condition(item) and is_rare_body_armour(item),
                   items)),
        'belts': list(
            filter(lambda item: condition(item) and is_rare_belt(item), items)),
        'rings': list(
            filter(lambda item: condition(item) and is_rare_ring(item), items)),
        'one_handed': list(filter(
            lambda item: condition(item) and is_rare_one_handed(item), items))
    }
    return ret


def _make_recipes(split):
    """
    Makes full set recipes from a given split of items.
    Args:
        split: Dictionary containing all available items for each item category

    Returns: An array of recipes.

    """
    recipes = []
    n_2h_weapon_sets = len(split['two_handed'])
    n_1h_weapon_sets = len(split['one_handed']) // 2
    weapon = \
        'two_handed' if n_2h_weapon_sets >= n_1h_weapon_sets else 'one_handed'
    N = min(
        len(split['amulets']), len(split['helmets']), len(split['gloves']),
        len(split['boots']),
        len(split['belts']),
        len(split['body_armour']),
        len(split['rings']) // 2,
        max(n_2h_weapon_sets, n_1h_weapon_sets))

    for i in range(0, N):
        recipe = [
            # 1x
            split['amulets'][i],
            split['helmets'][i],
            split['gloves'][i],
            split['boots'][i],
            split['belts'][i],
            split['body_armour'][i],
            # 2x
            split['rings'][2 * i],
            split['rings'][2 * i + 1]
        ]
        # Weapon
        if weapon == 'two_handed':
            recipe.append(split[weapon][i])
        else:
            recipe.append(split[weapon][2 * i])
            recipe.append(split[weapon][2 * i + 1])
        recipes.append(recipe)
    return recipes


def _make_influenced_set_recipe(items):
    recipes = []
    for influence in ItemInfluences:
        # For all possible influences try to make recipes.
        split = _split(items,
                       lambda item, influence=influence: item.has_influence(
                           influence))
        rs = _make_recipes(split)
        remove_recipe_items(rs, items)
        recipes.extend(rs)
    return recipes


def _try_replace_regal_recipe_item_with_chaos_recipe_item(r, items,
                                                          check_unidentified):
    """
    Tries to replace at least one item in the regal recipe with a chaos recipe
    item.
    Args:
        r: The regal recipe (Array of items)
        items: ALl the available items.
        check_unidentified: Whether to check for unidentified items while making
        chaos recipe.

    Returns: A modified regal recipe with some items replaced from chaos recipe
    set.

    """
    chaos_split = _split(items, chaos_recipe_condition(check_unidentified))

    # Find the item type with maximum number of items in chaos recipe items.
    item_type = max(chaos_split, key=lambda x: len(chaos_split[x]))

    if len(chaos_split[item_type]) == 0:
        return

    # Replace that item with regal recipes
    replacement = chaos_split[item_type][0]
    chaos_recipe_set_items_used = [replacement]

    if item_type == 'amulets':
        r[0] = replacement
        chaos_recipe_set_items_used = [replacement]
    elif item_type == 'helmets':
        r[1] = replacement
        chaos_recipe_set_items_used = [replacement]
    elif item_type == 'gloves':
        r[2] = replacement
        chaos_recipe_set_items_used = [replacement]
    elif item_type == 'boots':
        r[3] = replacement
        chaos_recipe_set_items_used = [replacement]
    elif item_type == 'belts':
        r[4] = replacement
        chaos_recipe_set_items_used = [replacement]
    elif item_type == 'body_armour':
        r[5] = replacement
        chaos_recipe_set_items_used = [replacement]
    elif item_type == 'rings':
        r[6] = replacement
        chaos_recipe_set_items_used = [replacement]
    elif item_type == 'two_handed':
        # Check if recipe has two one handed or one two handed items.
        if len(r) == 9:
            # Two handed, just replace.
            r[8] = replacement
            chaos_recipe_set_items_used = [replacement]
        else:
            # One handed. Replace one and remove other.
            r[8] = replacement
            chaos_recipe_set_items_used = [replacement]
            del r[-1]
    elif item_type == 'one_handed':
        # Check if recipe has two one handed or two one handed weapon
        if len(r) == 9:
            # Recipe has two handed. Remove the two handed and try to
            # add two one handed. This isn't optimal.
            if len(chaos_split[item_type]) > 1:
                # There is one more one handed available in chaos recipe
                # set.
                r[8] = replacement
                r.append(chaos_split[item_type][1])
                chaos_recipe_set_items_used = \
                    [replacement, chaos_split[item_type][1]]
            elif len(chaos_split['two_handed']) > 0:
                # There is only one one handed available in the chaos
                # recipe set. See if we have a two handed available in
                # the chaos recipe set and use that instead.
                r[8] = chaos_split['two_handed'][0]
                chaos_recipe_set_items_used = [chaos_split['two_handed'][0]]
        else:
            # One handed. Just replace one.
            r[8] = replacement
            chaos_recipe_set_items_used = [replacement]

    logger.debug(
        "Transformed a regal recipe into chaos recipe. Replaced {} item:{}"
        "".format(len(chaos_recipe_set_items_used), item_type))
    # Remove the items that we have used from the chaos recipe set from the
    # overall items array.
    remove_recipe_items([chaos_recipe_set_items_used], items)


def _make_regal_set_recipe(items):
    """
    This function doesn't really make regal set recipe, but tries to make chaos
    recipe, by replacing one item from the regal recipe with a chaos recipe one
    if it's available.
    Args:
        items:

    Returns:

    """

    def regal_recipe_helper(check_unidentified):
        split = _split(items, regal_recipe_condition(check_unidentified))
        rs = _make_recipes(split)
        for r in rs:
            # We replace regal recipe items with just 1 chaos recipe item as
            # pure regal recipes are less valuable than chaos recipes. Replacing
            # even 1 item, downgrades the recipe to chaos recipe.
            _try_replace_regal_recipe_item_with_chaos_recipe_item(
                r, items, check_unidentified)
        remove_recipe_items(rs, items)
        return rs

    # Try with unidentified items, then move to identified ones.
    recipes = regal_recipe_helper(True)
    recipes.extend(regal_recipe_helper(False))
    logger.debug("Created {} regal recipes".format(len(recipes)))
    return recipes


def chaos_recipe_condition(check_unidentified=False):
    def cond(item, check_unidentified=check_unidentified):
        if check_unidentified and item.is_identified():
            return False
        return FullSetRecipe.CHAOS_RECIPE_ITEM_LVL_MIN <= item.get_level() <= \
            FullSetRecipe.CHAOS_RECIPE_ITEM_LVL_MAX

    return cond


def regal_recipe_condition(check_unidentified=False):
    def cond(item, check_unidentified=check_unidentified):
        if check_unidentified and item.is_identified():
            return False
        return item.get_level() >= FullSetRecipe.REGAL_RECIPE_ITEM_LVL_MIN

    return cond


def _make_chaos_set_recipe(items):
    """
    Makes chaos recipes from a set of items. Also removes the created recipe
    items from the set.
    Args:
        items: A given set of items from which recipe is to be created.

    Returns: An array of recipes

    """

    def chaos_recipe_helper(check_unidentified):
        split = _split(items, chaos_recipe_condition(check_unidentified))
        rs = _make_recipes(split)
        remove_recipe_items(rs, items)
        return rs

    # Try with unidentified items, then move to identified ones.
    recipes = chaos_recipe_helper(True)
    recipes.extend(chaos_recipe_helper(False))
    logger.debug("Created {} chaos recipes".format(len(recipes)))
    return recipes


def sort_by_stash_position(a: StashItem, b: StashItem):
    if a.position[1] != b.position[1]:
        return -1 if a.position[1] < b.position[1] else 1
    else:
        return -1 if a.position[0] < b.position[0] else 1


class FullSetRecipe(Recipe):
    REGAL_RECIPE_ITEM_LVL_MIN = 75
    CHAOS_RECIPE_ITEM_LVL_MIN = 60
    CHAOS_RECIPE_ITEM_LVL_MAX = 74

    def __init__(self):
        super().__init__(vendor=True)

    def _apply(self, items: [StashItem]):
        if not items:
            return []
        recipes = []
        recipes.extend(_make_influenced_set_recipe(items))
        recipes.extend(_make_regal_set_recipe(items))
        recipes.extend(_make_chaos_set_recipe(items))
        for recipe in recipes:
            recipe = \
                sorted(recipe, key=functools.cmp_to_key(sort_by_stash_position))
        return recipes
