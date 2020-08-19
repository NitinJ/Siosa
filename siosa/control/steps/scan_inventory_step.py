import logging

import mss
import mss.tools

from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.control.game_step import Step
from siosa.data.stash import Stash
from siosa.image.inventory_scanner import InventoryScanner
from siosa.location.location_factory import LocationFactory, Locations


class ScanInventory(Step):
    def __init__(self, game_state):
        Step.__init__(self, game_state)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.clipboard = PoeClipboard()
        self.inventory_scanner = InventoryScanner()
        self.stash = Stash()
        self.items = []

    def execute(self):
        self.logger.info("Executing step: {}".format(self.__class__.__name__))
        item_positions = self.inventory_scanner.scan()
        for p in item_positions:
            self.mc.move_mouse(self._get_location(p))
            item = self.clipboard.read_item_at_cursor()
            stash_tabs = self.stash.get_stash_tabs_for_item(item)
            
            if not stash_tabs:
                raise Exception("Couldn't find a stash tab for item.")
            
            stash_tab = stash_tabs[0]
            
            self.logger.info("Stash tab for item:{!s} is:{!s}".format(
                item, stash_tab))
            
            self.items.append({
                'item': item,
                'position': p,
                'stash_tab': stash_tab,
            })
        self.game_state.update({'inventory': self.items})

    def _get_location(self, p):
        # Invent box size. + 3px border
        size_x = Locations.INVENTORY_0_0.get_width() + 3
        size_y = Locations.INVENTORY_0_0.get_height() + 3

        # Location of (0, 0)
        x, y = Locations.INVENTORY_0_0.get_center()

        x2 = x + p[1] * size_x
        y2 = y + p[0] * size_y
        return LocationFactory().create(x2, y2, x2, y2)
