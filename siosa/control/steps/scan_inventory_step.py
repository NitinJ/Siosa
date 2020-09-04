import logging

from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.control.game_step import Step
from siosa.data.inventory import Inventory
from siosa.data.stash import Stash
from siosa.image.inventory_scanner import InventoryScanner
from siosa.location.location_factory import LocationFactory, Locations


class ScanInventory(Step):
    def __init__(self):
        Step.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.clipboard = PoeClipboard()
        self.inventory_scanner = InventoryScanner()
        self.inventory_0_0 = self.lf.get(Locations.INVENTORY_0_0)
        self.stash = Stash()
        self.items = []

    def execute(self, game_state):
        self.game_state = game_state

        self.logger.info("Executing step: {}".format(self.__class__.__name__))
        item_positions = self.inventory_scanner.scan()
        for p in item_positions:
            self.mc.move_mouse(Inventory.get_location(p))
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
