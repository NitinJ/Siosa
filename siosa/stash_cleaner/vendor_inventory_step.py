import logging
import os
import time
from enum import Enum

from siosa.common.util import parent
from siosa.config.siosa_config import SiosaConfig
from siosa.control.game_state import GameState
from siosa.control.game_step import Step, StepStatus
from siosa.control.keyboard_controller import KeyboardController
from siosa.control.mouse_controller import MouseController
from siosa.data.currency_exchange import CurrencyExchange
from siosa.data.inventory import Inventory
from siosa.data.stash import Stash
from siosa.data.stash_item import StashItem
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.in_game_location import InGameLocation
from siosa.location.location_factory import Locations, LocationFactory
from siosa.network.poe_api import PoeApi
from siosa.stash_cleaner.recipies.test_recipe import TestRecipe


class Error(Enum):
    UNKNOWN = 0
    TANE_NOT_FOUND = 1


class VendorInventory(Step):
    SELL_WINDOW_OPEN_WAIT_TIME = 5

    def __init__(self, inventory: Inventory):
        """
        Args:
            inventory:
        """
        Step.__init__(self)
        self.inventory = inventory
        self.tm_tane = TemplateMatcher(TemplateRegistry.TANE.get())
        self.tm_trade_close_btn = \
            TemplateMatcher(TemplateRegistry.TRADE_WINDOW_CLOSE_BUTTON.get())

    def _open_tane_sell_window(self, location: InGameLocation):
        self.kc.hold_modifier('ctrl')
        self.mc.click_at_location(location)
        self.kc.unhold_modifier('ctrl')
        t1 = time.time()
        while time.time() - t1 < VendorInventory.SELL_WINDOW_OPEN_WAIT_TIME:
            if self.tm_trade_close_btn.match_exists(
                    self.lf.get(Locations.SCREEN_FULL)):
                return True
            time.sleep(0.1)
        return False

    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        self.game_state = game_state.get()
        if not self.inventory.items:
            return StepStatus(True)

        # Find tane.
        points = self.tm_tane.match(self.lf.get(Locations.SCREEN_FULL))
        if not points:
            return StepStatus(False, Error.TANE_NOT_FOUND)

        # Click on tane.
        tane_location = self.lf.create(
            points[0][0], points[0][1], points[0][0], points[0][1])
        if not self._open_tane_sell_window(tane_location):
            return StepStatus(False, Error.TANE_NOT_FOUND)

        game_state.update({'stash_location': None})

        # Loop over inventory and ctrl click on each item in order. Sort by
        # rows.
        self.kc.hold_modifier('ctrl')
        for pos in sorted(self.inventory.item_positions, key=lambda v: v[1]):
            self.mc.click_at_location(Inventory.get_location(pos))
        self.kc.unhold_modifier('ctrl')
        self.mc.click_at_location(
            self.lf.get(Locations.VENDOR_TRADE_ACCEPT_BUTTON))
        # Wait for trade window close animation.
        time.sleep(0.2)
        return StepStatus(True)


if __name__ == "__main__":
    FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(" \
             "funcName)s() ] %(message)s "
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    lf = LocationFactory()
    mc = MouseController(lf)
    kc = KeyboardController()
    exchange = CurrencyExchange(
        PoeApi("MopedDriverr", "0dfdc62a6d647095161d19e802961ef3",
               "Expedition"))
    config_file_path = os.path.join(parent(parent(parent(__file__))),
                                    "config.json")
    config = SiosaConfig.create_from_file(config_file_path)
    stash = Stash(config)
    stash_tab = stash.get_stash_tab_by_index(4)
    cells = stash_tab.get_item_cells_ingame()
    print(cells)

    stash_items = [
        StashItem.create_from(
            stash_tab.get_item_at_location(cell[0], cell[1]),
            stash_tab,
            (cell[1], cell[0])
        ) for cell in cells.keys()]
    stash_items = [item for item in stash_items if item]

    r = TestRecipe(stash_items)
    inventories = r.get_recipe_items()[:1]
    print(inventories)

    for inventory in inventories:
        kc.hold_modifier('ctrl')
        for item in inventory.items:
            stash_tab = item.stash_tab
            position = item.position
            mc.move_mouse(stash_tab.get_cell_location(position))
            # Don't actually sell.
            # mc.click()
        kc.unhold()

    step = VendorInventory(inventories[0])
    gs = GameState()
    step.execute(gs)
