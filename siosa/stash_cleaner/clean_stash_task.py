import logging
import time

from siosa.common.decorations import override
from siosa.control.game_task import Task
from siosa.control.keyboard_controller import KeyboardController
from siosa.control.mouse_controller import MouseController
from siosa.control.steps.change_stash_tab_step import ChangeStashTab
from siosa.control.steps.clean_inventory_step import CleanInventory
from siosa.control.steps.close_all_windows_step import CloseAllWindows
from siosa.control.steps.open_stash_step import OpenStash
from siosa.control.steps.scan_inventory_step import ScanInventory
from siosa.data.stash import Stash
from siosa.data.stash_item import StashItem
from siosa.data.stash_tab import StashTabType
from siosa.image.inventory_scanner import InventoryScanner
from siosa.location.location_factory import LocationFactory
from siosa.stash_cleaner.recipies.full_set_recipe import FullSetRecipe
from siosa.stash_cleaner.recipies.simple_recipe import get_gem_recipe, \
    get_flask_recipe, get_vendor_recipe, get_deposit_recipe
from siosa.stash_cleaner.vendor_inventory_step import VendorInventory


class CleanStashTask(Task):
    def __init__(self, stash_index):
        """
        Args: stash_index to clean
        """
        Task.__init__(self, 8, name='CleanStashTask', stop_on_step_failure=True)
        self.stash_index = stash_index
        self.stash_tab = Stash().get_stash_tab_by_index(self.stash_index)
        self.recipes = [get_gem_recipe(), get_flask_recipe(), FullSetRecipe(),
                        get_vendor_recipe(), get_deposit_recipe()]
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.kc = KeyboardController()
        self.lf = LocationFactory()
        self.mc = MouseController(self.lf)

    def _get_items(self):
        cells = self.stash_tab.get_item_cells_ingame()
        stash_items = [
            StashItem.create_from(
                self.stash_tab.get_item_at_location(cell[1], cell[0]),
                self.stash_tab,
                (cell[0], cell[1])
            ) for cell in cells.keys()]
        return [item for item in stash_items if item]

    def _transfer_items_to_inventory(self, inventory):
        self.kc.hold_modifier('ctrl')
        for item in inventory.items:
            stash_tab = item.stash_tab
            position = item.position
            self.mc.move_mouse(stash_tab.get_cell_location(position))
            self.mc.click()
        self.kc.unhold()

    def _deposit_inventory(self):
        def deposit():
            self.kc.hold_modifier('ctrl')
            self.mc.click()
            self.kc.unhold_modifier('ctrl')
        inventory = InventoryScanner().get_inventory(callback=deposit)

    def get_steps(self):
        if self.stash_tab.get_type() != StashTabType.UNKNOWN:
            self.logger.debug("Unsupported stash tab type")
            return

        yield OpenStash()
        yield ChangeStashTab(self.stash_index)
        time.sleep(1)
        items = self._get_items()
        for recipe in self.recipes:
            self.logger.debug("Running recipe: {}".format(recipe))
            inventories = recipe.get_recipe_items(items)
            for inventory in inventories:
                self._transfer_items_to_inventory(inventory)
                if recipe.vendor:
                    yield CloseAllWindows()
                    yield VendorInventory(inventory)
                    yield OpenStash()
                    self._deposit_inventory()
                else:
                    yield ScanInventory()
                    yield CleanInventory()

    @override
    def _cleanup_internal(self):
        OpenStash().execute(self.game_state)
        ChangeStashTab(self.stash_index).execute(self.game_state)
        self._deposit_inventory()
        ChangeStashTab(0).execute(self.game_state)
