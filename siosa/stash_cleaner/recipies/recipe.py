from siosa.data.inventory import Inventory
from siosa.data.stash_item import StashItem
from siosa.stash_cleaner.recipies.util import remove_recipe_items


class Recipe:
    def __init__(self, vendor=False):
        self.vendor = vendor

    def get_recipe_items(self, items: [StashItem]):
        """
        Returns: The items in the recipe in the form of inventory objects. Each
        inventory object represents one iteration of a recipe over the set of
        items.

        """
        # An array of arrays
        if not items:
            return []

        recipes = self._apply(items)
        remove_recipe_items(recipes, items)

        inventory_objs = []
        for recipe in recipes:
            # Try to fit each recipe into an inventory. If not, split into
            # multiple inventories.
            if not recipe:
                continue
            inventory = Inventory()
            for item in recipe:
                if not inventory.add_item(item):
                    inventory_objs.append(inventory)
                    inventory = Inventory()
                    inventory.add_item(item)
            inventory_objs.append(inventory)
        return inventory_objs

    def _apply(self, items):
        """
        Filters a list of items and returns sets of items that can make the
        recipe.
        Args:
            items: The list of items from which to create the recipe

        Returns: An array of arrays of items. Each array represents one recipe
        set of items. If items from an array cannot fit into one inventory,
        they will be split into multiple inventory objects. Even if an array
        doesn't have enough items to fill in an inventory, a new inventory is
        created for it.
        E.g - If [[gem1,gem2...gem100]], then multiple (3 here in the eg)
        inventory objects will be created.

        """
        raise NotImplementedError()

    def is_vendor_recipe(self):
        return self.vendor
