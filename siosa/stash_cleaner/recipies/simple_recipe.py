from siosa.data.stash_item import StashItem
from siosa.stash_cleaner.recipies.recipe import Recipe
from siosa.stash_cleaner.recipies.util import should_vendor_item


class SimpleRecipe(Recipe):
    def __init__(self, condition, vendor=True):
        super().__init__(vendor=vendor)
        self.condition = condition

    def _apply(self, items: [StashItem]):
        recipe = [item for item in items if self.condition(item)]
        return [] if not recipe else [recipe]


def get_flask_recipe():
    return SimpleRecipe(lambda item: item.is_flask())


def get_vendor_recipe():
    return SimpleRecipe(lambda item: should_vendor_item(item))


def get_gem_recipe():
    return SimpleRecipe(lambda item: item.is_gem())


def get_deposit_recipe():
    return SimpleRecipe(
        lambda item: not should_vendor_item(item), vendor=False)
